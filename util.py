# -*- coding: iso-8859-1 -*-

import os
import signal
import re
import time
import socket
import sys
from Crypto.PublicKey import RSA
from Crypto.Hash import MD5
from Crypto.Util import randpool
import cPickle
import pwd

all_nodes = ["node%02d" % i for i in xrange(1,39)]

TIMEOUT = 2
FIRST_PORT = 8001
LAST_PORT = 8099
UTIL_DEBUGLEVEL = 0

MANAGER_IP = "192.168.4.1"
MANAGER_PORT = 8000
MANAGER_ADDR = (MANAGER_IP,MANAGER_PORT)
SCHEDULER_PORT = 8100

NETWORK_BUFFER_SIZE = 1024

rpool = randpool.RandomPool()
rpool.add_event("%lf"%time.time())

signedMessagePattern = re.compile(r'<SignedMessage(?:(?:\s+user="(?P<user>\w+)")?|(?:\s+sig=(?P<sig>[\dAaBbCcDdEeFf]+))?){2,2}>\s*(?P<msg>[\w\W]*?)\s*</SignedMessage>')

def SetDebugLevel(debuglevel):
    global UTIL_DEBUGLEVEL
    UTIL_DEBUGLEVEL = debuglevel

def createDaemon():
   """Detach a process from the controlling terminal and run it in the
   background as a daemon.

   Author: Chad J. Schroeder
   """

   try:
      # Fork a child process so the parent can exit.  This will return control
      # to the command line or shell.  This is required so that the new process
      # is guaranteed not to be a process group leader.  We have this guarantee
      # because the process GID of the parent is inherited by the child, but
      # the child gets a new PID, making it impossible for its PID to equal its
      # PGID.
      pid = os.fork()
   except OSError, e:
      return((e.errno, e.strerror))     # ERROR (return a tuple)

   if (pid == 0):       # The first child.

      # Next we call os.setsid() to become the session leader of this new
      # session.  The process also becomes the process group leader of the
      # new process group.  Since a controlling terminal is associated with a
      # session, and this new session has not yet acquired a controlling
      # terminal our process now has no controlling terminal.  This shouldn't
      # fail, since we're guaranteed that the child is not a process group
      # leader.
      os.setsid()

      # When the first child terminates, all processes in the second child
      # are sent a SIGHUP, so it's ignored.
      signal.signal(signal.SIGHUP, signal.SIG_IGN)

      try:
         # Fork a second child to prevent zombies.  Since the first child is
         # a session leader without a controlling terminal, it's possible for
         # it to acquire one by opening a terminal in the future.  This second
         # fork guarantees that the child is no longer a session leader, thus
         # preventing the daemon from ever acquiring a controlling terminal.
         pid = os.fork()        # Fork a second child.
      except OSError, e:
         return((e.errno, e.strerror))  # ERROR (return a tuple)

      if (pid == 0):      # The second child.
         # Ensure that the daemon doesn't keep any directory in use.  Failure
         # to do this could make a filesystem unmountable.
         os.chdir("/")
         # Give the child complete control over permissions.
         os.umask(0)
      else:
         os._exit(0)      # Exit parent (the first child) of the second child.
   else:
      os._exit(0)         # Exit parent of the first child.

   # Close all open files.  Try the system configuration variable, SC_OPEN_MAX,
   # for the maximum number of open files to close.  If it doesn't exist, use
   # the default value (configurable).
   try:
      maxfd = os.sysconf("SC_OPEN_MAX")
   except (AttributeError, ValueError):
      maxfd = 256       # default maximum

   for fd in range(0, maxfd):
      try:
         os.close(fd)
      except OSError:   # ERROR (ignore)
         pass

   # Redirect the standard file descriptors to /dev/null.
   os.open("/dev/null", os.O_RDONLY)    # standard input (0)
   os.open("/dev/null", os.O_RDWR)       # standard output (1)
   os.open("/dev/null", os.O_RDWR)       # standard error (2)

   return(0)

def SwitchUser(new_user):
    f = open('/etc/passwd','r')
    uid = [l.split(':')[2] for l in f.xreadlines() if l.startswith("%s:"%new_user)]
    f.close()
    uid = int(uid[0])
    os.setuid(uid)

def SendMessage(message,address):
    if UTIL_DEBUGLEVEL & 1:
	print "to %s: %s" % (address[0],message)
	sys.stdout.flush()
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.sendto(message,address)
    sock.close()

def ReceiveMessage(address,bufflen=512):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    sock.bind(address)
    (ans,addr) = sock.recvfrom(bufflen)
    sock.close()
    return ans,addr

def GetListenSocket(address="",timeout=0):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    port = FIRST_PORT
    success = False
    while port <= LAST_PORT and not success:
	try:
	    sock.bind((address,port))
	    success = True
	except socket.error,e:
	    if e[0] == 98: #Adress already in use
		port += 1

    if timeout:
	sock.settimeout(timeout)

    if success:
	return sock,port
    else:
	raise socket.error((98,'Address already in use'))

def CreateKey(fname=None):
    rpool.add_event("%lf"%time.time())
    key = RSA.generate(512,rpool.get_bytes)
    if fname:
	f = open(fname,'w')
	cPickle.dump(key,f)
	f.close()
	os.chmod(fname,0600)
	f = open(fname+".pub",'w')
	cPickle.dump(key.publickey(),f)
	f.close()
	os.chmod(fname+".pub",0644)
    return key

def LoadKey(fname):
    f = open(fname,'r')
    key = cPickle.load(f)
    f.close()
    return key

def SignMessage(message):
    hash = MD5.new(message).digest()
    pwdentry = pwd.getpwuid(os.geteuid())
    user = pwdentry[0]
    if user == "cluster":
	keyfile = '/etc/cluster_key'
    else:
	keyfile = os.path.join(pwdentry[5],".cluster_key")
    key = LoadKey(keyfile)
    sig = key.sign(hash,"")
    out_msg = '<SignedMessage user="%s" sig="%X">%s</SignedMessage>' % (user,sig[0],message)
    return out_msg

def VerifySignedMessage(message):
    m = signedMessagePattern.match(message)
    if not m:
	return ""
    hash = MD5.new(m.group("msg")).digest()
    pwdentry = pwd.getpwnam(m.group("user"))
    user = pwdentry[0]
    if user == 'cluster':
	keyfile = '/etc/cluster_key.pub'
    else:
	keyfile = os.path.join(pwdentry[5],".cluster_key.pub")
    key = LoadKey(keyfile)
    if key.verify(hash,(int(m.group("sig"),16),)):
	return m.group("msg")
    return ""

def VerifySignedMessage2(message,user,sig):
    hash = MD5.new(message).digest()
    pwdentry = pwd.getpwnam(user)
    user = pwdentry[0]
    if user == 'cluster':
	keyfile = '/etc/cluster_key.pub'
    else:
	keyfile = os.path.join(pwdentry[5],".cluster_key.pub")
    key = LoadKey(keyfile)
    if key.verify(hash,(int(sig,16),)):
	return message
    return ""

def SendTCPMessage(message,sock):
    if UTIL_DEBUGLEVEL & 1:
	print "to %s: %s" % (sock.getpeername()[0],message)
	sys.stdout.flush()
    # Quebra a mensagem em "pedaços" com o tamanho do buffer de rede
    li = []
    start = 0
    while True:
	end = start + NETWORK_BUFFER_SIZE - 3 # len('...')
	if len(message) <= end + 3:
	    li.append(message[start:])
	    break
	else:
	    li.append(message[start:end] + '...' )
	start += NETWORK_BUFFER_SIZE - 3

    for str in li:
	#print str
	sock.send(str)

def GetTCPMessage(sock):
    message = ""
    while True:
	m = sock.recv(NETWORK_BUFFER_SIZE)
	if m.endswith('...'):
	    message += m[:-3]
	else:
	    message += m
	    break

    if UTIL_DEBUGLEVEL & 1:
	print "from %s: %s" % (sock.getpeername()[0],message)
	sys.stdout.flush()
    return message

def do_nothing(arg=""):
    pass

if __name__ == "__main__":
    message = "Teste de funcionamento"
    print "Mensagem original:\n%s\n" % message
    signed_message = SignMessage(message)
    print "Após assinatura:\n%s\n" % signed_message
    verified_message = VerifySignedMessage(signed_message)
    print "Após verificação:\n%s\n" % verified_message
