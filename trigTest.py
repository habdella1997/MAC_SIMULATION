
angleTilt = 18
p1x = 445
p1y = 680
p2x = 700
p2y = 600 

apx = 0
apy = 0 

p1_l2 = p1x - apx
p1_l1 = p1y - apy

p2_l2 = p2x - apx
p2_l1 = p2y - apy

import math
p1_refAngle = 2 * math.degrees(math.atan2(p1_l2 , p1_l1) )  
p1_refAngle_xaxis = (90) + ( p1_refAngle/2)  -(angleTilt)

p1_slope = math.tan(math.radians(p1_refAngle_xaxis))
p1_intercept = p1y - p1_slope*p1x


print("slope m1 : " + str(algo_m1))

p2_refAngle = 2 * math.degrees(math.atan2(p2_l2 , p2_l1) ) - (2*angleTilt)
p2_refAngle_xaxis = (90 + p2_refAngle/2) - angleTilt
p2_slope = math.tan(math.radians(p2_refAngle_xaxis))
p2_intercept = p2y - p2_slope*p2x

print("P1 Ref Angle: " + str(p1_refAngle))
print("P1 Slope: "     + str(p1_slope))
print("P1 y intercept: " + str(p1_intercept))
print("P1 x intercept: " + str(-1*p1_intercept / p1_slope))


print("P2 Ref Angle: " + str(p2_refAngle))
print("P2 Slope: "     + str(p2_slope))
print("P2 y intercept: " + str(p2_intercept))
print("P2 x intercept: " + str(-1*p2_intercept / p2_slope))