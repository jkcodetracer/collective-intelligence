#!/usr/bin/python

from pylab import *

a = array([1,2,3,4])
b = array([4,2,3,1])
plot(a,b)
show()

t1 = arange(0.0, 10.0, 0.1)
plot(t1, sin(t1))
show()
