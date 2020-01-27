# time step calculation
import math as m
l = 2.0       # mesh_size in mm
e = 210000.0    # youngs modulus N/mm2
ro = 7.89e-09 # density tonne/mm3

c = m.sqrt(e/ro)
delT = l/c

print "time step =", delT, "seconds"
