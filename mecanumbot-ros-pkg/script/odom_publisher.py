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

        self.m=tf.TransformBroadcaster()
        self.odom_pub = rospy.Publisher("odom", Odometry, queue_size=50)
        
        self.t = geometry_msgs.msg.TransformStamped()
        self.t.header.frame_id = 'odom'
        #t.header.stamp = rospy.Time(0)
        self.t.child_frame_id = 'base_link'
        self.t.transform.translation.x = 0
        self.t.transform.translation.y = 0
        self.t.transform.translation.z = 0
        self.t.transform.rotation.w=0
        self.t.transform.rotation.x=0
        self.t.transform.rotation.y=0
        self.t.transform.rotation.z=0

        self.odom=Odometry()
        self.odom.header.frame_id = "odom"
        self.odom.child_frame_id = "base_link"

        self.r = rospy.Rate(10.0)

    def callback(self,encoders):
#over tf
        self.curtime=rospy.Time.now()
        dt = (self.curtime - self.pretime).to_sec()
        
        dx = encoders.linear.x*dt
        dy = encoders.linear.y*dt
        dth = encoders.angular.z*dt
        self.th += dth
        self.th = math.fmod(self.th, 2*math.pi)

        self.x += dx * math.cos(self.th) - dy * math.sin(self.th)
        self.y += dx * math.sin(self.th) + dy * math.cos(self.th)

        self.t.header.stamp =  rospy.Time.now()
        q=tf.transformations.quaternion_from_euler(0,0,self.th)
        self.t.transform.translation.x = self.x
        self.t.transform.translation.y = self.y
        self.t.transform.translation.z = 0
        self.t.transform.rotation.w=q[3]
        self.t.transform.rotation.x=q[0]
        self.t.transform.rotation.y=q[1]
        self.t.transform.rotation.z=q[2]
        self.m.sendTransformMessage(self.t)
        print self.t
# over ros
        self.odom.header.stamp = self.curtime
    # set the position
        self.odom.pose.pose = Pose(Point(self.x, self.y, 0.), Quaternion(*q))
    # set the velocity
        self.odom.twist.twist = Twist(Vector3(encoders.linear.x, encoders.linear.y, 0), Vector3(0, 0, encoders.angular.z))
    # publish the message
        self.odom_pub.publish(self.odom)

        self.pretime = self.curtime #要保证不停地发指令，即使不运动
        self.r.sleep()


    def run(self):
        rospy.Subscriber('/cmd_vel', Twist, self.callback)
        rospy.spin()

if __name__=='__main__':
    rospy.init_node('odom_publisher', anonymous=False)
    en=encoder()
    en.run()