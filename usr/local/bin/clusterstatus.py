#!/usr/bin/env python

import wx, sys, os

#...................................................................
# Para o WindowsXP
if wx.Platform == '__WXMSW__':
    try: 
        f = open('C:\Python24\clusterstatus.rc')
    except:
        f = open('C:\Python24\clusterstatus_1.0\etc\clusterstatus.rc')
	          
    sys.path.append('C:\Python24\clusterstatus_1.0\lib') # diretorio que contem os arquivos para importar
    MYBITMAP = 'C:\Python24\clusterstatus_1.0\share\loadbar2.bmp'

# Para o Linux
if wx.Platform == '__WXGTK__':
    HOME = os.environ.get('HOME')
    try: 
        f = open(HOME+'/.clusterstatus.rc') 
    
    except:
        f = open(HOME+'/etc/clusterstatus/clusterstatus.rc')  

   
    sys.path.append(HOME+'/usr/local/lib/clusterstatus')  

    MYBITMAP = HOME+'/usr/local/share/clusterstatus/loadbar2.bmp'  
    
#....................................................................
from Numeric import sum
import client_tools

#....................................................................
# Leitura do arquivo de configuracao 
NNO = f.readline()
while NNO[0:3]!='NNO': 
    NNO = f.readline()
  
    TIMER = f.readline()
while TIMER[0:5]!='TIMER':
    TIMER = f.readline()
  
NNO = int(NNO[6:-1])
TIMER_REFRESH = int(TIMER[8:-1])

#....................................................................
# Defines
BGCOLOR = '#F0F0F0'
BGBARCOLOR = '#F5F5F5'
DEADTEXTCOLOR = '#B0B0B0'
TEXTCOLOR = '#000000'
SELBGCOLOR = '#0D0DBF'
SELTEXTCOLOR = '#FFFFFF'
LINE_SIZE = 16

#....................................................................
def TDrawRectangle(dc, rectangle, color=BGCOLOR):
    pen = [ wx.Pen(color) ]
    brush = [ wx.Brush(color) ]
    dc.DrawRectangleList( [rectangle], pen, brush )

#....................................................................
def TDrawText(dc, text, point, foreground=TEXTCOLOR, background=BGCOLOR):
    foreground = [ wx.NamedColor(foreground) ]
    background = [ wx.NamedColor(background) ]
    dc.DrawTextList([text], [point], foreground, background)

#....................................................................
def RedrawHeader(dc):
    cW = dc.GetCharWidth()
    dc.SetFont(wx.Font(8, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD ))
    
    TDrawRectangle( dc, (2, 2, 422, 20) )
        
    string_list = ['Name', 'Load']
    points_list = [(20,4), (80,4)]
    foregrounds = [ wx.NamedColour( TEXTCOLOR ) ]*2
    backgrounds = [ wx.NamedColour( BGCOLOR ) ]*2 
    dc.DrawTextList( string_list, points_list, foregrounds, backgrounds )
        
    dc.SetFont(wx.Font(8, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ))
    
    string_list = ['0 %', '100 %', '50 %']
    points_list = [(120,4), ( 420-cW*4,4), ( (420-150-cW*3),4)]
    foregrounds = [ wx.NamedColour( TEXTCOLOR ) ]*3
    backgrounds = [ wx.NamedColour( BGCOLOR ) ]*3 
    dc.DrawTextList( string_list, points_list, foregrounds, backgrounds )

#....................................................................
def ReDrawNode(dc, nObj, nno):
    cW = dc.GetCharWidth()
    dc.SetFont(wx.Font(8, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ))

    line = nObj.line[nno]
    ypos = LINE_SIZE*line+6
    NCpus = len(nObj.NodeStatus[nno]) - 1
    
    if not nObj.IsDead[nno]:
        if nObj.IsSelected[nno]:
            TDrawRectangle( dc, (2,ypos,422,LINE_SIZE), SELBGCOLOR)
        else:
            TDrawRectangle( dc, (2,ypos,422,LINE_SIZE))
            
        if nObj.NodeStatus[nno][0]!=100:
            if nObj.IsSelected[nno]:
		if nObj.NodeStatus[nno][0] < 10:   
                    TDrawText( dc, ' ' + str(nObj.NodeStatus[nno][0]) + " %", (110-cW*4,ypos+2), SELTEXTCOLOR, SELBGCOLOR)
	        else:
		    TDrawText( dc, str(nObj.NodeStatus[nno][0]) + " %", (110-cW*4,ypos+2), SELTEXTCOLOR, SELBGCOLOR)
            else:
		if nObj.NodeStatus[nno][0] < 10:    
                    TDrawText( dc, ' ' + str(nObj.NodeStatus[nno][0]) + " %", (110-cW*4,ypos+2))
	        else:
		    TDrawText( dc, str(nObj.NodeStatus[nno][0]) + " %", (110-cW*4,ypos+2))
        else:
            if nObj.IsSelected[nno]:
                TDrawText( dc, str(nObj.NodeStatus[nno][0]) + " %",(110-cW*5,ypos+2), SELTEXTCOLOR, SELBGCOLOR)
            else:
                TDrawText( dc, str(nObj.NodeStatus[nno][0]) + " %",(110-cW*5,ypos+2))
            
        if nObj.IsSelected[nno]:
            TDrawText( dc, nObj.nNames[nno], (20,ypos+2), SELTEXTCOLOR,SELBGCOLOR)                
        else:
            TDrawText( dc, nObj.nNames[nno], (20,ypos+2))

        dc.DrawBitmap( nObj.LoadBar, 120, ypos+2)
            
        TDrawRectangle( dc, (120+3*nObj.NodeStatus[nno][0], ypos+2,300-3*nObj.NodeStatus[nno][0], LINE_SIZE-4), BGBARCOLOR )
            
    else:
        if nObj.ShowDead:
            if nObj.IsSelected[nno]:
                TDrawRectangle( dc, (2, ypos, 422, LINE_SIZE), SELBGCOLOR)
            else:
                TDrawRectangle( dc, (2, ypos, 422, LINE_SIZE))   
           
            if nObj.IsSelected[nno]:
                dc.SetTextBackground( wx.NamedColor(SELBGCOLOR) )
            else:
                dc.SetTextBackground( wx.NamedColor(BGCOLOR) )
            dc.SetTextForeground( wx.NamedColor(DEADTEXTCOLOR) )                   
            dc.DrawText( nObj.nNames[nno], 20, ypos+2 )
            dc.DrawText( 'D E A D', 120, ypos+2 )            
        
    TDrawRectangle( dc, (2, ypos, LINE_SIZE, LINE_SIZE) )
        
    if not nObj.IsDead[nno]:
        dc.SetPen(wx.Pen(TEXTCOLOR))
        dc.SetBrush(wx.Brush(BGCOLOR))
        dc.DrawRectangle(4, ypos+2, 9, 9)
      
        dc.DrawLine( 6, ypos+6, 11, ypos+6)
        
        if nObj.IsExpanded[nno]:
            if nObj.IsSelected[nno]:
		k=1
		while k <= NCpus:  
                    TDrawRectangle( dc, (2, ypos+LINE_SIZE*k, 422, LINE_SIZE), SELBGCOLOR )
                    k+=1
		dc.SetTextForeground( wx.NamedColor(SELTEXTCOLOR) )
                dc.SetTextBackground( wx.NamedColor(SELBGCOLOR) )

            else:    
		k=1
		while k <= NCpus:    
                    TDrawRectangle( dc, (2, ypos+LINE_SIZE*k, 422, LINE_SIZE) )
                    k+=1    
                dc.SetTextForeground( wx.NamedColor(TEXTCOLOR) )
                dc.SetTextBackground( wx.NamedColor(BGCOLOR) )
            
	    k=1
	    while k <= NCpus:  
		TDrawRectangle( dc, (2, ypos+LINE_SIZE*k, LINE_SIZE, LINE_SIZE) )    
	        dc.DrawText( 'CPU ' + str(k-1), 20, ypos+LINE_SIZE*k)
		dc.DrawBitmap( nObj.LoadBar, 120, ypos+LINE_SIZE*k+2)
		TDrawRectangle( dc, (120+3*nObj.NodeStatus[nno][k],ypos+LINE_SIZE*k+2, 300-3*nObj.NodeStatus[nno][k], LINE_SIZE-4),BGBARCOLOR )
		k+=1
	    
	    points_y = []
            points_x = []
            dc.SetPen( wx.Pen(TEXTCOLOR) )
	    
            for i in range(NCpus*8-1):
                points_y.append( (8, ypos+12+i*2) )
            
	    k=1
	    while k <= NCpus:
	        for i in range(3):
                    points_x.append( (10+i*2, ypos+LINE_SIZE*k+8) )
		k+=1
		
            dc.DrawPointList( points_y )
            dc.DrawPointList( points_x )
		    
        else:
            dc.DrawLine( 8, ypos+4, 8, ypos+9)       

#.................................................................... 
class TNodeObject:
    def __init__(self, scrolledWindow):
        self.scrolledWindow = scrolledWindow
	    
        self.nNames = [0]*(NNO)
        self.NodeStatus = [0]*(NNO)    
        self.LoadBar = wx.Bitmap(MYBITMAP)
	    
        self.ShowDead = True     
        self.IsExpanded = [False]*(NNO)
        self.IsSelected = [False]*(NNO)
        self.IsDead = [False]*(NNO)
       
        self.area = [0]*NNO
        self.line = [1]*NNO
        self.line_previous = [1]*NNO
        self.IsExpanded_previous = [0]*NNO
	
        # controle caso o cluster nao esteja funcionando
        self.TRY = True
        self.cont_try = 0
    
        self.__get_Info()
        
    def __get_Info(self):
        self.line = [1]*NNO
        self.IsDead = [False]*NNO
        self.area = [0]*NNO
        
	# Recebe as informacoes do cluster
        if self.TRY:
            try:
                self.CpuLoads = client_tools.QueryCpuLoads(('192.168.2.21', 8000))
            except:
                self.CpuLoads = {}
                self.TRY = False
        
        elif not self.cont_try==15:
            self.CpuLoads = {}
            self.cont_try += 1
        else:
            self.CpuLoads = {}
            self.cont_try = 0
            self.TRY = True
        
        for i in range(NNO):
	    # Nomeia todos os nos 	
            if i >= 9:   
                self.nNames[i] = 'node'+str(i+1)
            else:
                self.nNames[i] = 'node0'+str(i+1)
		
	    # Atribui 'DEAD' aos nos nao recebidos	
            if self.CpuLoads.has_key(self.nNames[i]):
                self.NodeStatus[i] = self.CpuLoads[self.nNames[i]]
            else:
                self.NodeStatus[i] = 'DEAD'
            
            if self.NodeStatus[i]=='DEAD':
                self.IsDead[i] = True
                self.IsExpanded[i] = False
            
	    # Determina a linha em que sera desenhado o noh 
            if i:
                if self.ShowDead:
                    if self.IsExpanded[i-1]:
                        self.line[i] = self.line[i-1] + len(self.NodeStatus[i-1])
                    else:
                        self.line[i] = self.line[i-1] + 1
                else:
                    if self.IsDead[i-1]:
                        self.line[i] = self.line[i-1]
                    elif self.IsExpanded[i-1]:
                        self.line[i] = self.line[i-1] + len(self.NodeStatus[i-1])
                    else:
                        self.line[i] = self.line[i-1] + 1
	# Determina quais linhas pertecem a cada noh		
        for i in range(NNO):
            if i==(NNO-1):
                self.area[i] = range(self.line[i], self.line[i]+(len(self.NodeStatus[i])-1)*self.IsExpanded[i]+1*(not self.IsExpanded[i])+1)
            else:
                self.area[i] =  range(self.line[i], self.line[i+1])
    
    # Redesenha o DC
    def ReDrawDC(self, dc, LoadDisplay):
        self.__get_Info()
        
        RedrawHeader(dc)
                
        for i in range(NNO):
            if self.ShowDead:
                ReDrawNode(dc, self, i)
            elif not self.IsDead[i]:
                ReDrawNode(dc, self, i)   
        
        self.line_previous = self.line
        self.IsExpanded_previous = self.IsExpanded             

#....................................................................
class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'cluster.status', size=wx.Size(450, 480))
        self.scrolledWindow = MyScrolledWindow(self)
        
        self.__set_StatusBar()  
        self.__set_Properties()
        self.__set_Timer()

    def Reposition(self, statusBar):
        if wx.Platform == '__WXMSW__':
            rect = statusBar.GetFieldRect(0)
        if wx.Platform == '__WXGTK__':  
            rect = statusBar.GetFieldRect(1)

        statusBar.cb.SetPosition((rect.x+2, rect.y+2))
        statusBar.cb.SetSize((rect.width-4, rect.height-4))
        statusBar.sizeChanged = False
 
    def __set_Properties(self):
        self.Bind(wx.EVT_TIMER, self.TimerEvent)
        self.scrolledWindow.Bind(wx.EVT_LEFT_UP, self.MouseEvent )
        self.SetStatusBar(self.statusBar)
        self.Reposition(self.statusBar)
        self.Show(True)
        self.Refresh()
 
    def __set_StatusBar(self):
        self.statusBar = wx.StatusBar(self, -1)
        self.statusBar.sizeChanged = False
        self.statusBar.cb = wx.CheckBox(self.statusBar, 1001, "Show Dead Node")
        self.statusBar.Bind(wx.EVT_CHECKBOX, self.CheckBoxEvent, self.statusBar.cb)
        self.statusBar.cb.SetValue(self.scrolledWindow.NodeObject.ShowDead)
        
    def __set_Timer(self):
        self.timer = wx.Timer(self)
        self.timer.Start(TIMER_REFRESH) 
    
    def TimerEvent(self, evenvt):
        #print self.scrolledWindow.NodeObject.NodeStatus[52]
        self.Refresh()
        
    def CheckBoxEvent(self, event):
        if self.statusBar.cb.GetValue():
            self.scrolledWindow.NodeObject.ShowDead = True
        else:
            self.scrolledWindow.NodeObject.ShowDead = False
        self.Refresh()
        
    def MouseEvent(self, event):
        pos = event.GetPosition() + (0, self.scrolledWindow.GetScrollPos(1)*200)
        node = self.NodeClicked(pos)

        if (pos[0] > 14) & (node[0]!=None):
            if self.scrolledWindow.NodeObject.IsSelected[node[0]]:
                self.scrolledWindow.NodeObject.IsSelected[node[0]] = False
            else:
                self.scrolledWindow.NodeObject.IsSelected[node[0]] = True
        
        elif (node[0]!=None):
            if not self.scrolledWindow.NodeObject.IsDead[node[0]]: 
                if (self.scrolledWindow.NodeObject.IsExpanded[node[0]]):
                    if node[1]==0:
                        self.scrolledWindow.NodeObject.IsExpanded[node[0]] = False
                else:
                    self.scrolledWindow.NodeObject.IsExpanded[node[0]] = True     
        self.Refresh()
 
    def NodeClicked(self, pos):
        if pos[0]<422:
            yl = int((pos[1]-22)/16) +1
            for i in range(NNO):
                lenght = len(self.scrolledWindow.NodeObject.area[i])  
                for j in range(lenght):
                    if yl==self.scrolledWindow.NodeObject.area[i][j]:
                        return [i, self.scrolledWindow.NodeObject.area[i][j]-self.scrolledWindow.NodeObject.area[i][0]]  
	    
        return [None]
      
#....................................................................
class MyScrolledWindow(wx.ScrolledWindow):
    def __init__(self, frame):
        wx.ScrolledWindow.__init__(self, frame, -1, style=wx.VSCROLL)
        self.SetScrollbars(0, 200, 0, 500, True)
        self.SetBackgroundColour(wx.WHITE)

        self.NodeObject = TNodeObject(self)   
        self.NodeObject.drawFun = self.NodeObject.ReDrawDC
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        self.NodeObject.drawFun(dc, self)
        self.NodeObject.drawFun = self.NodeObject.ReDrawDC
        
#....................................................................
class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.frame = MyFrame()
        self.SetTopWindow(self.frame)
        self.frame.Bind( wx.EVT_CLOSE, self.OnCloseFrame )
        return 1

    def OnCloseFrame(self, event):
        self.frame.Show(False)
        self.Exit()   
           
#..........................................................
# Executa a aplicacao
if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
