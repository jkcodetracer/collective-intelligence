#!/usr/bin/python

from random import random, randint
import math

def euclidean(v1, v2):
	d = 0.0
	for i in range(len(v1)):
		d+=(v1[i]-v2[i])**2
	return math.sqrt(d)

def wineprice(rating, age):
	peak_age = rating-50

	# caculate price based on rating
	price = rating/2
	if age>peak_age:
		# goes bad in 5 years
		price = price * (5-(age-peak_age))
	else:
		price = price * (5*((age+1)/peak_age))
	if price<0:
		price = 0
	return price

def wineset1():
	rows = []
	for i in range(300):
		# create a random age and rating
		rating = random()*50 + 50
		age = random()*50

		price = wineprice(rating, age)
		price *= (random()*0.4 + 0.8)

		rows.append({'input':(rating,age),
			'result':price})

	return rows

def getdistances(data, vec1):
	distancelist = []
	for i in range(len(data)):
		vec2 = data[i]['input']
		distancelist.append((euclidean(vec1, vec2), i))
	distancelist.sort()
	return distancelist

def knnestimate(data, vec1, k=3):
	# get sorted distance
	dlist = getdistances(data, vec1)
	avg = 0.0

	# take the average of top k results
	for i in range(k):
		idx = dlist[i][1]
		avg += data[idx]['result']
	avg = avg/k
	return avg

print wineprice(95.0, 3.0)
print wineprice(95.0, 8.0)
print wineprice(99.0, 1.0)
data = wineset1()
print data[0]
print data[1]
print data[0]['input'],data[1]['input']
print euclidean(data[0]['input'], data[1]['input'])
print knnestimate(data, (95.0, 3.0))
print knnestimate(data, (99.0, 3.0))
print knnestimate(data, (99.0, 5.0))
print wineprice(99.0, 5.0)
print knnestimate(data, (99.0, 5.0), k=1)


