#!/usr/bin/python

from random import random, randint
from pylab import *
import math
import sys

def rescale(data, scale):
	scaleddata = []
	for row in data:
		scaled = [scale[i]*row['input'][i] for i in range(len(scale))]
		scaleddata.append({'input':scaled, 'result':row['result']})

	return scaleddata

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

def wineset2():
	rows = []
	for i in range(300):
		rating = random()*50+50
		age = random()*50
		aisle = float(randint(1,20))
		bottlesize = [375.0, 750.0, 1500.0, 3000.0][randint(0,3)]
		price = wineprice(rating, age)
		price *= (bottlesize/750)
		price *= (random()*0.9+0.2)
		rows.append({'input':(rating, age, aisle,bottlesize),
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
	total = 0.0
	totalweight = 0.0

	for i in range(k):
		dist = dlist[i][0]
		idx = dlist[i][1]
		total += dist
		weight = weightf(dist)
		if weight == 0.0:
			continue
		avg += weight*data[idx]['result']
		totalweight += weight
	if totalweight == 0.0:
		avg = total/k
	else:
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

def createcostf(algf, data):
	def costf(scale):
		sdata = rescale(data, scale)
		return crossvalidate(algf, sdata, trials = 1)
	return costf

def probguess(data, vec1, low, high, k = 5, weightf = gaussian):
	dlist = getdistances(data, vec1)
	nweight = 0.0
	tweight = 0.0

	for i in range(k):
		dist = dlist[i][0]
		idx = dlist[i][1]
		weight = weightf(dist)
		v = data[idx]['result']

		if v >= low and v <= high:
			nweight += weight
		tweight += weight
	if tweight == 0:
		return 0
	return nweight/tweight

def cumulativegraph(data, vec1, high, k=5, weightf=gaussian):
	t1 = arange(0.0, high, 0.1)
	cprob = array([probguess(data, vec1, 0, v, k, weightf) for v in t1])
	plot(t1, cprob)
	show()

def probabilitygraph(data, vec1, high, k=5, weightf = gaussian, ss=2.0):
	t1 = arange(0.0, high, 0.1)

	probs = [probguess(data, vec1, v, v+0.1, k, weightf) for v in t1]

	# smooth them by adding the gaussian of the nearby probabilities
	smoothed = []
	for i in range(len(probs)):
		sv = 0.0
		for j in range(len(probs)):
			dist = abs(i-j) * 0.1
			weight = gaussian(dist, sigma = ss)
			sv += weight*probs[j]
		smoothed.append(sv)
	smoothed = array(smoothed)

	plot(t1, smoothed)
	show()

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

print "---test probability guess---"
print probguess(data, [99,20], 40,80)
print probguess(data, [99,20], 80,120)
print probguess(data, [99,20], 120,1000)
print probguess(data, [99,20], 80,240)

cumulativegraph(data, [95,20], 150)
probabilitygraph(data, [95,20], 150)

print '--- test cross validation --- '
print crossvalidate(knn3,data)
print crossvalidate(knn1,data)

print '--- test heterogeneous valuables---'
heterogeneous = wineset2()
print crossvalidate(knn3, heterogeneous)
print crossvalidate(weightedknn, heterogeneous)

print '--- test rescale ---'
rescaleddata = rescale(heterogeneous, [1,1,0,0.25])
print crossvalidate(knn3, rescaleddata)
print crossvalidate(weightedknn, rescaleddata)


'''
sys.path.append('/Users/codetracer/JustForFun/AI/collective_intelligence/optimization')
import optimization

print '--- optimization with annealing---'
costf = createcostf(weightedknn, heterogeneous)
domain = [(0,20)]*4
s = optimization.annealingoptimize(domain, costf)
print s
rescaleddata = rescale(heterogeneous, s)
print crossvalidate(weightedknn, rescaleddata)

print '--- optimization with genetic---'
costf = createcostf(weightedknn, heterogeneous)
gen = optimization.genetic()
s = gen.geneticoptimize(domain, costf)
print s
rescaleddata = rescale(heterogeneous, s)
print crossvalidate(weightedknn, rescaleddata)
'''


