#!/usr/bin/python

from numpy import *

def difcost(a,b):
	dif = 0
	# loop all the rows and column in the matrix
	for i in range(shape(a)[0]):
		for j in range(shape(a)[1]):
			# add together the differences
			dif += pow(a[i,j] - b[i,j], 2)
	return dif

def factorize(v, pc = 10, iter = 50):
	ic = shape(v)[0]
	fc = shape(v)[1]

	# initialize the weight and feature matrices with random values
	w = matrix([[random.random() for j in range(pc)] for i in range(ic)])
	h = matrix([[random.random() for i in range(fc)] for j in range(pc)])

	# perform operation a maximum of iter times
	for i in range(iter):
		wh = w*h

		# calculate the current difference
		cost = difcost(v, wh)

		if i%10 == 0:
			print cost

		# terminate if done
		if cost == 0: break

		# update feature matrix
		hn = (transpose(w)*v)
		hd = (transpose(w)*w*h)

		h = matrix(array(h) * array(hn)/array(hd))

		# update weights matrix
		wn = (v*transpose(h))
		wd = (w*h*transpose(h))

		w = matrix(array(w)*array(wn)/array(wd))
	
	return w,h


print '--- test nmf---'
m1 = matrix([[1,2,3], [4,5,6]])
m2 = matrix([[1,2],[3,4],[5,6]])
print m1,m2

w,h = factorize(m1*m2, pc = 3, iter = 100)
print w*h
print m1*m2

