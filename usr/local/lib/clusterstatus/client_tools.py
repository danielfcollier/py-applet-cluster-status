# -*- coding: iso-8859-1 -*-

import socket
import exceptions
import re
import os.path
import getopt
import sys
import util

all_nodes = ["node%02d" % i for i in xrange(1,40)]
TIMEOUT = 5

default_options_string = '''\
-h,--help: Mostra esse texto
-f,--file arq: Usa arq como arquivo de opções (padrão é ~/.cluster_tools.conf)'''

# program_help: Dicionário contendo as seguintes chaves:
# program_help["arguments"] -> Descrição dos argumentos do programa
# program_help["commandline"] -> Exemplo da linha de comando
# program_help["description"] -> Descrição do programa
# program_help["options"] -> Descrição das opções do programa

class ServerError(exceptions.Exception):
    def __init__(self,args=None):
	self.args = args

def ShowHelp(program_help):
    if program_help.has_key("commandline"):
	print program_help["commandline"]
	print
    if program_help.has_key("description"):
	print "Descrição:"
	for line in program_help["description"].strip().split('\n'):
	    print "  " + line
	print
    if program_help.has_key("arguments"):
	print "Argumentos:"
	for line in program_help["arguments"].strip().split('\n'):
	    print "  " + line
	print
    print "Opções:"
    options_string = ""
    if program_help.has_key("options"):
	options_string += program_help["options"].strip()
    options_string += "\n"+default_options_string
    for line in options_string.strip().split('\n'):
	print "  " + line

def GetOptions(argv,program_help,options='',long_options=[]):
    program_name = os.path.basename(argv.pop(0))
    if program_name.endswith('.py'):
	program_name = program_name[0:-3]

    try:
	opts,args = getopt.getopt(argv,'hf:'+options,['--help','--file=']+long_options)
    except getopt.GetoptError,err:
	print "ERRO: %s" % err
	sys.exit(0)

    opts_0 = [o[0] for o in opts]

    if '-h' in opts_0 or '--help' in opts_0:
	ShowHelp(program_help)
	sys.exit(0)

    if '-f' in opts_0 or '--file' in opts_0:
	options_file = [o[1] for o in opts if '-f' in o or '--file' in o].pop()
    else:
	options_file = '~/.cluster_tools.conf'

    argv = GetUserOptions(program_name,options_file) + argv

    try:
	opts,args = getopt.getopt(argv,'hf:'+options,['--help','--file=']+long_options)
    except getopt.GetoptError,err:
	print "ERRO: %s" % err
	sys.exit(0)

    return opts,args

def GetUserOptions(tool,filename="~/.cluster_tools.conf"):
    filename = os.path.expanduser(filename)
    try:
	file = open(filename,'r')
    except IOError:
	return []

    valid_options = [l for l in file.xreadlines() if l.strip().startswith(tool)]
    file.close()
    valid_options = map(lambda x:x.split(':')[1].strip(),valid_options)
    valid_options = map(lambda x:x.split(),valid_options)
    user_options = reduce(lambda x,y:x+y,valid_options,[])

    return user_options

def QueryAliveNodes(server_address,nodes_list=[]):
    if len(nodes_list) == 0:
	nodes_list_string = ''
    else:
	nodes_list_string = reduce(lambda x,y: x+","+y,nodes_list)

    (RecvSock,port) = util.GetListenSocket(address="",timeout=TIMEOUT)
    QueryMessage = '<Query port="%d">NodesAlive(%s)</Query>'%(port,nodes_list_string)
    util.SendMessage(QueryMessage,server_address)
    (answer,addr) = RecvSock.recvfrom(1024)
    RecvSock.close()

    AnswerPat = re.compile(r'<Answer>\s*NodesAlive\((?P<msg>[\w\s\.,=]*)\)\s*;\s*</Answer>')
    m = AnswerPat.match(answer)
    if m != None:
	alive_nodes = m.group("msg").split(',')
    else:
	raise ServerError, "Resposta do servidor inválida!"

    return alive_nodes

def QueryDeadNodes(server_address):
    alive_nodes = QueryAliveNodes(server_address)
    dead_nodes = [ node for node in all_nodes if node not in alive_nodes ]

    return dead_nodes

def QueryCpuLoads(server_address,nodes_list=[]):
    if len(nodes_list) == 0:
	nodes_list_string = ''
    else:
	nodes_list_string = reduce(lambda x,y: x+","+y,nodes_list)

    (RecvSock,port) = util.GetListenSocket(address="",timeout=TIMEOUT)
    QueryMessage = '<Query port="%d">CpuLoads(%s)</Query>'%(port,nodes_list_string)
    util.SendMessage(QueryMessage,server_address)
    (answer,addr) = RecvSock.recvfrom(2048)
    RecvSock.close()

    AnswerPat = re.compile(r'<Answer>\s*CpuLoads\((?P<msg>[\w\s\.,=]*)\)\s*;\s*</Answer>')
    m = AnswerPat.match(answer)
    cpu_loads = {}
    if m != None:
	l = [ tuple(item.split("=")) for item in m.group("msg").split(',')]
	for i in l:
	    cpu_loads[i[0]] = [int(j) for j in i[1].split()]
    else:
	raise ServerError, "Resposta do servidor inválida!"

    return cpu_loads

def QueryClusterJobs(server_address):
    (RecvSock,port) = util.GetListenSocket(address="",timeout=TIMEOUT)
    QueryMessage = '<Query port="%d">Jobs()</Query>'%(port)
    util.SendMessage(QueryMessage,server_address)
    (answer,addr) = RecvSock.recvfrom((128*1024))
    RecvSock.close()

    AnswerPat = re.compile(r'<Answer>\s*Jobs\((?P<msg>[\w\W]*)\)\s*;\s*</Answer>')
    m = AnswerPat.match(answer)
    if m != None:
	jobs = m.group("msg").split(',')
	jobs = [j.split(":") for j in jobs]
    else:
	raise ServerError, "Resposta do servidor inválida!"

    sortfunc = lambda x,y: cmp(int(x[0]),int(y[0]))
    jobs.sort(sortfunc)
    return jobs
    
if __name__ == "__main__":
    server_address = ('192.168.2.21',8000)
    alive_nodes = QueryAliveNodes(server_address)
    dead_nodes = QueryDeadNodes(server_address)
    cpu_loads = QueryCpuLoads(server_address)
    user_options = GetUserOptions('cluster.all','sample_cluster_tools.conf')

    f = lambda x,y: str(x)+' '+str(y)
    print "Nós ligados:"
    print reduce(f, alive_nodes)
    print
    print "Nós desligados:"
    print reduce(f, dead_nodes)
    print
    print "Carga das CPUs:"
    cpu_loads = ["%s %s" % (node,reduce(f,cpu_loads[node])) for node in cpu_loads.keys()]
    cpu_loads.sort()
    print reduce(lambda x,y: x+'\n'+y,cpu_loads)
    print
    print "Opções padrão da ferramenta cluster.all:"
    print reduce(f,user_options,'').strip()

