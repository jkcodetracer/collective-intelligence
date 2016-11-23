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

def inverseweight(dist, num = 1.0, const = 0.1):
	return num/(dist+const)

def subtractweight(dist, const = 1.0):
	if dist > const:
		return 0
	else:
		return const-dist

def gaussian(dist, sigma = 1.0):
	return math.e**(-1*(dist**2)/(2*(sigma**2)))

def weightedknn(data, vec1, k=5, weightf=gaussian):
	dlist = getdistances(data, vec1)
	avg = 0.0
	totalweight = 0.0

	for i in range(k):
		dist = dlist[i][0]
		idx = dlist[i][1]
		weight = weightf(dist)
		avg += weight*data[idx]['result']
		totalweight += weight
	avg = avg/totalweight
	return avg

# for cross-validation
def dividedata(data, test = 0.05):
	trainset = []
	testset = []
	for row in data:
		if random() < 0.05:
			testset.append(row)
		else:
			trainset.append(row)
	return trainset, testset

def testalgorithm(algf, trainset, testset):
	error = 0.0
	for row in testset:
		guess = algf(trainset, row['input'])
		error += (row['result']-guess)**2
	# get the variation
	return error/len(testset)

def crossvalidate(algf, data, trials = 100, test=0.05):
	error = 0.0
	for  i in range(trials):
		trainset,testset = dividedata(data,test)
		error += testalgorithm(algf,trainset,testset)

	return error/trials

def knn3(d,v):
	return knnestimate(d,v,k=3)

def knn1(d,v):
	return knnestimate(d,v,k=1)


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

print '---test weight function---'
print subtractweight(0.1)
print inverseweight(0.1)
print gaussian(0.1)
print gaussian(1.0)
print subtractweight(1)
print inverseweight(1)
print gaussian(3.0)
print "---test weight knn---"
print weightedknn(data, (95.0, 3.0))
print weightedknn(data, (99.0, 3.0))
print weightedknn(data, (99.0, 5.0))

print '--- test cross validation --- '
print crossvalidate(knn3,data)
print crossvalidate(knn1,data)

