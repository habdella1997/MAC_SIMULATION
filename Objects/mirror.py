class mirror:
    id = 0
    def __init__(self, length, angleTilt,c_x,c_y ):
        self.length    = length
        self.angleTilt = angleTilt
        self.xCorP1    = 0
        self.yCorP1    = 0
        self.xCorP2    = 0
        self.yCorP2    = 0
        self.p1_slope  = 0
        self.p1_y_int  = 0 
        self.c_x = c_x
        self.c_y = c_y
        self.m_1 = 0
        self.m_2 = 0
        self.fov_1_y = []
        self.fov_2_y = []
        self.fov_1_x = []
        self.fov_2_x = []
        self.fov_1_y_intercept = 0
        self.fov_2_y_intercept = 0
        self.id = mirror.id
        mirror.id += 1