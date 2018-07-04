import os
import numpy as np

class Position:
    def __init__(self,x_st,y_st,*arg):
        #init global oordinate system
        self.st_pos_x=x_st
        self.st_pos_y=y_st
        self.st_dir_v=arg
   
    def deg2vec(deg):
        return np.cos(deg/180.0*np.pi),np.sin(deg/180.0*np.pi)

    def 




