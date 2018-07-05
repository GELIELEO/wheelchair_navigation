#coding:utf-8
import pygame
from pygame.locals import *
from pygame_button import button
from pygame_label import label
from pygame_anchors import anchors
from pygame_textbox import textbox
from vector import vector2D
import time
from serial import Serial
from MecanumBase import MecanumBase
import numpy as np
import sys,os

VELTRANSLATE = 45 #40
VELROTATE = 3 #2.5

script_path = os.path.split(sys.argv[0])[0]

class GUI_mecanum:
    """
    author:mrtang
    date:2017.7
    version:1.0
    email:mrtang@nudt.edu.cn
    """

    def __init__(self,com):
        self.MD = MecanumBase()
        self.cmdbuf = self.MD.stop()
        self.cmd = 0
        self.cmdstr = [u'停止',u'平移',u'旋转',u'复合']
        self.seropened = False
        self.ser = None
        self.mp = (0,0)
        self.effective = 0
        self.driving = False
        self.center = vector2D(216,213)
        self.tag = 0

        self.END =0
        pygame.init()
        self.scr = pygame.display.set_mode((537,429),0,32)
        self.background = pygame.image.load(script_path+'background.jpg').convert()

        self.label = label(self.scr,(460,30),'left',text=u'端口:',textsize=13,forecolor=(0,0,0,0),textcolor=(255,255,0),textfont='stsong')
        self.textbox = textbox(self.scr,(460+self.label.getsize()[0],30),anchor='left',siz = (32,20),textcolor=(255,0,0),forecolor=(200,200,200,255),cusorcolor=(255,0,0))
        self.textbox.focused = 1
        self.label2 = label(self.scr,(460,60),'left',text=u'未连接',textsize=13,forecolor=(0,0,0,0),textfont='stsong',textcolor=(255,255,0),borderon=1,bordercolor = (255,255,255,255))
        self.openbt = button(self.scr,(460,90),'left',(60,25),textsize = 15,bordercolor=(0,0,255),forecolor=(200,200,200,255),text = u'连接',textcolor=(255,255,0),textfont='stsong')
        self.cmdlabel = label(self.scr,(460,120),'left',text=u'停止',textsize=13,forecolor=(0,0,0,0),textcolor=(255,255,0),borderon=1,bordercolor = (255,255,255,255),textfont='stsong')
        self.transbt = button(self.scr,(460,150),'left',(60,25),textsize = 15,bordercolor=(0,0,255),forecolor=(200,200,200,255),text = u'平移',textcolor=(255,255,0),textfont='stsong')
        self.rotatebt = button(self.scr,(460,180),'left',(60,25),textsize = 15,bordercolor=(0,0,255),forecolor=(200,200,200,255),text = u'旋转',textcolor=(255,255,0),textfont='stsong')
        self.stopbt = button(self.scr,(216,213),'center',(60,60),textsize = 30,bordercolor=(0,0,255),forecolor=(200,200,200,0),text = u'停止',textcolor=(255,255,0),textfont='stsong')
        self.mulbt = button(self.scr,(460,210),'left',(60,25),textsize = 15,bordercolor=(0,0,255),forecolor=(200,200,200,255),text = u'复合',textcolor=(255,255,0),textfont='stsong')

		
        self.cursorlabel = label(self.scr,(0,0),'lefttop',text='',textsize=15,forecolor=(0,0,0,255),textcolor=(255,255,255),textfont='stsong',borderon = 0,visible = False)

        self.clk = pygame.time.Clock()

    def openbtcallback(self):
        if not self.seropened:
            try:
                self.ser = Serial('COM%s'%(self.textbox.gettext),115200)
                self.cmdbuf = self.MD.setPort('wireless')
                self.seropened = 1
                self.label2.text = u'已连接'
                self.openbt.text = u'断开'
            except:
                self.label2.text = u'连接失败'
        else:
            self.ser.close()
            self.seropened = 0
            self.label2.text = u'已断开'
            self.openbt.text = u'连接'

    def transbtcallback(self):
        self.cmd = 1
        self.cmdlabel.text = self.cmdstr[self.cmd]

    def rotatebtcallback(self):
        self.cmd = 2
        self.cmdlabel.text = self.cmdstr[self.cmd]

    def mulbtcallback(self):
	    #self.tag = 0;
     


        self.cmd = 3
        self.cmdlabel.text = self.cmdstr[self.cmd]
    def stopbtcallback(self):
        self.driving = False
        self.cmd = 0
        self.cmdlabel.text = self.cmdstr[self.cmd]
        self.cmdbuf = self.MD.stop()
        self.cursorlabel.vsible = False

    def direct_measure(self,d):
        d.Y = -d.Y
        a = int(d.Angle*180/np.pi-90)
        a1 = a if a>=0 else 360+a  #0-360
        a2 = a if a>-90 and a<=180 else a-360
        return a1,a2

    def run(self):
        global VELTRANSLATE
        global VELROTATE
        T_R=0
        while True:
            self.center = vector2D(216,213)
            ev = pygame.event.get()
            for e in ev:
                if e.type == QUIT:  self.END = 1

            self.scr.blit(self.background,(0,0))
            self.label.update()
            self.label2.update()
            self.cmdlabel.update()
            self.cursorlabel.update()

            self.textbox.update(ev)
            self.openbt.update(ev,self.openbtcallback)
            self.transbt.update(ev,self.transbtcallback)
            self.rotatebt.update(ev,self.rotatebtcallback)
            self.stopbt.update(ev,self.stopbtcallback)
            self.mulbt.update(ev,self.mulbtcallback)
			

            if self.seropened:
                if not self.driving:
                    for e in ev:
                        if e.type == MOUSEMOTION:
                            self.mp = e.pos
                            self.mpv = vector2D(self.mp[0],self.mp[1])-self.center
                            if self.mpv.Len>55 and self.mpv.Len<210:
                                a1,a2 = self.direct_measure(self.mpv)
                                self.cursorlabel.visible = 1
                                self.cursorlabel.position = self.mp
                                if self.cmd == 1:
                                    self.tag=0
                                    self.cursorlabel.text = u'平移 x:'+str(int(self.mpv.X))+' y:'+str(int(self.mpv.Y))
                                elif self.cmd == 2:
                                    self.tag=0
                                    self.cursorlabel.text = u'旋转'+str(int(a2))+u'度'
                                elif self.cmd == 3:
                                    if self.tag ==0:
                                        self.cursorlabel.text = u'平移 x:'+str(int(self.mpv.X))+' y:'+str(int(self.mpv.Y))
                                    else:
                                        self.cursorlabel.text = u'已选择平移到 x:'+str(x)+' y:'+str(y)+u'旋转'+str(int(a2))+u'度'  
                                else:
                                    self.cursorlabel.visible = False
                            else:
                                self.cursorlabel.visible = 0

                        elif e.type == MOUSEBUTTONUP:
                            self.mp = e.pos
                            self.mpv = vector2D(self.mp[0],self.mp[1])-self.center
                            if self.mpv.Len>55 and self.mpv.Len<210:
                                a1,a2 = self.direct_measure(self.mpv)
                                if self.cmd == 1:
                                    VELTRANSLATE=50
                                    VELROTATE=3.5
                                    self.cmdbuf = self.MD.translateV(VELTRANSLATE,int(a1))
                                    self.lstclk = time.clock()
                                    self.endclk = self.lstclk+4*self.mpv.Len/VELTRANSLATE
                                    self.driving = True
                                elif self.cmd == 2:
                                    VELTRANSLATE=50
                                    VELROTATE=3.5
                                    self.cmdbuf = self.MD.rotateV(-VELROTATE*np.sign(a2))
                                    self.lstclk = time.clock()
                                    self.endclk = self.lstclk+abs(a2)/VELROTATE
                                    self.driving = True
                                elif self.cmd == 3:
                                    self.tag = 1
                                    VELTRANSLATE=50
                                    VELROTATE=3.5
                                    x=int(self.mpv.X)
                                    y=int(self.mpv.Y)
                                    self.lstclk = time.clock()
                                    t1=10*self.mpv.Len/VELTRANSLATE
                                    t2=abs(a2)/VELROTATE
                                    t=max(t1,t2)
                                    print t
                                    self.endclk=self.lstclk+t
                                    VELTRANSLATE=10*self.mpv.Len/t
                                    VELROTATE=abs(a2)/t
                                    print VELTRANSLATE,VELROTATE
                                    self.driving=True
                                    #pygame.draw.circle(self.scr,(255,0,0),self.mp,5)                                   
                                else:
                                    self.cmdbuf = self.MD.stop()
                else:
                    pygame.draw.circle(self.scr,(255,0,0),self.mp,5)
                    if time.clock()-self.endclk>0:
                        self.driving = False
                        self.cmdbuf = self.MD.stop()
                        self.cursorlabel.visible=False
                    elif self.cmd == 3:
                        #print "a1:",a1
                       # print "v:",VELTRANSLATE
                        #self.cmdbuf = self.MD.mul_temp(VELTRANSLATE,int(a1),-VELROTATE*np.sign(a2))
                        a1=a1-VELROTATE*np.sign(a2)*(1/30.0)
                        self.cmdbuf = self.MD.mul(VELTRANSLATE,int(a1),-VELROTATE*np.sign(a2))
                self.ser.write(self.cmdbuf)

            pygame.display.update()
            self.clk.tick(30)
            

            if self.END:    break
        if self.seropened:
            self.cmdbuf = self.MD.stop()
            for i in range(20):
                self.ser.write(self.cmdbuf)
                time.sleep(0.05)
            self.ser.close()
        self.ser.close()
        pygame.quit()

if __name__ == '__main__':
    k =  GUI_mecanum(3)
    k.run()
