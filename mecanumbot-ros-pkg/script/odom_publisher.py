#!/usr/bin/env python
#coding=utf-8

import math
import time
import rospy
from geometry_msgs.msg import *
import tf2_ros.transform_broadcaster
import tf
from nav_msgs.msg import Odometry
'''
undo the encoder feedback,assume that every cmd
can be executed,and read the vel per x seconds

'''
class encoder:
    def __init__(self):
        #self.pretime=rospy.rostime.get_time()
        #self.curtime=rospy.rostime.get_time()
        self.curtime = rospy.Time.now()
        self.pretime = rospy.Time.now()
        self.x=0
        self.y=0
        self.th=0
        self.vx=0
        self.vy=0
        self.vth=0

        self.m=tf.TransformBroadcaster()
        self.odom_pub = rospy.Publisher("/odom", Odometry, queue_size=50)
        rospy.Subscriber('/cmd_vel', Twist, self.callback)
        
        self.t = geometry_msgs.msg.TransformStamped()
        self.t.header.frame_id = 'odom'
        self.t.header.stamp = rospy.Time.now()
        self.t.child_frame_id = 'base_link'
        self.t.transform.translation.x = 0
        self.t.transform.translation.y = 0
        self.t.transform.translation.z = 0
        q=tf.transformations.quaternion_from_euler(0,0,0)
        '''
        self.t.transform.rotation=q
        '''
        self.t.transform.rotation.w=q[3]
        self.t.transform.rotation.x=q[0]
        self.t.transform.rotation.y=q[1]
        self.t.transform.rotation.z=q[2]

        self.odom=Odometry()
        self.odom.header.frame_id = "odom"
        self.odom.child_frame_id = "base_link"
        self.odom.header.stamp = rospy.Time.now()
        self.odom.pose.pose.position.x = 0
        self.odom.pose.pose.position.y = 0
        self.odom.pose.pose.position.z = 0
        self.odom.pose.pose.orientation.x=0
        self.odom.pose.pose.orientation.y=0
        self.odom.pose.pose.orientation.z=0
        self.odom.pose.pose.orientation.w=1
        self.odom.twist.twist.linear.x = 0
        self.odom.twist.twist.linear.y = 0
        self.odom.twist.twist.angular.z = 0      
        
        self.r = rospy.Rate(5.0)

    def callback(self,encoders):
#over tf
        #self.curtime=rospy.Time.now()
        
        self.vx = encoders.linear.x
        self.vy = encoders.linear.y
        self.vth = encoders.angular.z
        
        self.t.header.stamp =  rospy.Time.now()
        q=tf.transformations.quaternion_from_euler(0,0,self.th)
        self.t.transform.translation.x = self.x
        self.t.transform.translation.y = self.y
        self.t.transform.translation.z = 0
        self.t.transform.rotation.w=q[3]
        self.t.transform.rotation.x=q[0]
        self.t.transform.rotation.y=q[1]
        self.t.transform.rotation.z=q[2]  
# over ros
        self.odom.header.stamp = rospy.Time.now()
        self.odom.pose.pose = Pose(Point(self.x, self.y, 0.), Quaternion(*q))
        self.odom.twist.twist = Twist(Vector3(encoders.linear.x, encoders.linear.y, 0), Vector3(0, 0, encoders.angular.z))


        #self.r.sleep()

    def run(self):
        while 1:
            #一定要记得更新时间 一定要记得更新时间 一定要记得更新时间！！！
            self.curtime=rospy.Time.now()
            self.t.header.stamp = rospy.Time.now()
            self.odom.header.stamp = rospy.Time.now()
            
            dt = (self.curtime - self.pretime).to_sec()
            
            dx=self.vx*dt
            dy=self.vy*dt
            dth=self.vth*dt

            self.th += dth
            self.th = math.fmod(self.th, 2*math.pi)
            self.x += dx * math.cos(self.th) - dy * math.sin(self.th)
            self.y += dx * math.sin(self.th) + dy * math.cos(self.th)
            
            self.m.sendTransformMessage(self.t)
            self.odom_pub.publish(self.odom)
            
            self.vx=0
            self.vy=0
            self.vth=0

            self.pretime=self.curtime
            #print self.t
            self.r.sleep()

if __name__=='__main__':
    rospy.init_node('odom_publisher', anonymous=True)
    en=encoder()
    en.run()