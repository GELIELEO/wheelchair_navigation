#!/usr/bin/env python
#coding=utf-8
import rospy
import math
from MecanumBase import MecanumBase
from geometry_msgs.msg import Twist
from serial import Serial
import numpy as np

#defined by chan: 
#unit: TRAN:m/s || ROT:d/s
#frame: Right_Hand gun
#       top layer design   x:^ y:<
#       low layer design   x:> y:^ 

class MBnode:
    def __init__(self):
        self.mb = MecanumBase()
    #回调函数输入的应该是msg
    def callback(self,cmd):
        #distance = math.sqrt(math.pow(cmd.linear.x, 2)+math.pow(cmd.linear.y, 2)) 
        #rospy.loginfo('running....')
        if cmd.angular.z == 0: #进行平移运动
            tempv=int(1000*(math.sqrt(math.pow(cmd.linear.x, 2)+math.pow(cmd.linear.y, 2))))
            tempd=self.dir_tf_TRAN(cmd)
            self.cmdbuf=self.mb.translateV(tempv,tempd)
        elif cmd.linear.x==0 and cmd.linear.y==0:#进行旋转运动
            self.cmdbuf=self.mb.rotateV(cmd.angular.z)
        self.ser.write(self.cmdbuf)

    def dir_tf_TRAN(self,d): #0~360 从y轴开始，顺时针
        tempy=d.linear.x
        tempx=-d.linear.y
        tempd=math.atan(tempy/(tempx+1e-6))
        tempd = int(tempd*180/np.pi-90)
        a1 = tempd if tempd>=0 else 360+tempd  #0-360
        #a2 = a if a>-90 and a<=180 else a-360
        return a1

    def listener(self):
        rospy.init_node('cmd_listener', anonymous=True)
        try:
            self.ser = Serial('/dev/ttyUSB0',115200)
            self.cmdbuf = self.mb.setPort('wireless')
            self.ser.write(self.cmdbuf)
            rospy.loginfo('已连接\n')
        except:
            rospy.loginfo('连接失败\n')
        #Subscriber函数第一个参数是topic的名称，第二个参数是接受的数据类型 第三个参数是回调函数的名称
        rospy.Subscriber('/cmd_vel_mux/input/teleop', Twist, self.callback)
        rospy.spin()

if __name__ == '__main__':
    mbapp = MBnode()
    mbapp.listener()

