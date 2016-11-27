#!/usr/bin/python

import math 

class matchrow:
	def __init__(self, row, allnum=False):
		if allnum:
			self.data = [float(row[i]) for i in range(len(row)-1)]
		else:
			self.data = row[0:len(row)-1]
		self.match = int(row[len(row)-1])

def yesno(v):
	if v == 'yes':
		return 1
	elif v == 'no':
		return -1
	else:
		return 0
def matchcount(interest1, interest2):
	l1 = interest1.split(':')
	l2 = interest2.split(':')
	x = 0
	for v in l1:
		if v in l2:
			x += 1
	return x

def milesdistance(a1, a2):
	return 0


def loadmatch(f, allnum=False):
	rows = []
	for line in file(f):
		rows.append(matchrow(line.split(','), allnum))
	return rows

def loadnumerical():
	oldrows = loadmatch('matchmaker.csv')
	newrows = []

	for row in oldrows:
		d = row.data
		data = [float(d[0]), yesno(d[1]), yesno(d[2]),
			float(d[5]), yesno(d[6]), yesno(d[7]),
			matchcount(d[3], d[8]),
			milesdistance(d[4],d[9]),
			row.match]
		newrows.append(matchrow(data))
	return newrows

# put all the value in [0,1]
def scaledata(rows):
	low = [999999999.0]*len(rows[0].data)
	high = [-999999999.0]*len(rows[0].data)

	for row in rows:
		d = row.data
		for i in range(len(d)):
			if d[i] < low[i]:
				low[i] = d[i]
			if d[i] > high[i]:
				high[i] = d[i]

	# create a function that scales data
	def scaleinput(du):
		output = []
		for i in range(len(low)):
			if high[i] == low[i]:
				output += [0]
			else:
				output += [(du[i]-low[i])/(high[i]-low[i])]
		return output

	newrows = [matchrow(scaleinput(row.data) + [row.match])
			for row in rows]

	return newrows, scaleinput

def lineartrain(rows):
	averages = {}
	counts = {}

	for row in rows:
		cl = row.match

		averages.setdefault(cl, [0.0]*len(row.data))
		counts.setdefault(cl, 0)

		for i in range(len(row.data)):
			averages[cl][i] += float(row.data[i])

		counts[cl] += 1
	
	for cl,avg in averages.items():
		for i in range(len(avg)):
			avg[i]/=counts[cl]

	return averages

def dotproduct(v1,v2):
	return sum([v1[i]*v2[i] for i in range(len(v1))])

def dpclassify(point, avgs):
	b = (dotproduct(avgs[1], avgs[1]) - dotproduct(avgs[0], avgs[0]))/2
	y = dotproduct(point, avgs[0])-dotproduct(point, avgs[1])+b
	if y > 0:
		return 0
	else:
		return 1

# the kernel mehod
def veclength(vec):
	return math.sqrt(sum([v*v for v in vec]))

# radial-basis function
def rbf(v1, v2, gamma = 20):
	dv = [v1[i] - v2[i] for i in range(len(v1)) ]
	l = veclength(dv)
	return math.e**(-gamma*l)

def nlclassify(point, rows, offset, gamma = 10):
	sum0 = 0.0
	sum1 = 0.0
	count0 = 0
	count1 = 0

	for row in rows:
		if row.match == 0:
			sum0 += rbf(point, row.data, gamma)
			count0 += 1
		else:
			sum1 += rbf(point, row.data, gamma)
			count1 += 1
	y = (1.0/count0)*sum0 - (1.0/count1)*sum1 + offset

	if y > 0:
		return 0
	else:
		return 1

def getoffset(rows, gamma = 10):
	l0 = []
	l1 = []

	for row in rows:
		if row.match == 0:
			l0.append(row.data)
		else:
			l1.append(row.data)
	sum0 = sum(sum([rbf(v1, v2, gamma) for v1 in l0]) for v2 in l0)
	sum1 = sum(sum([rbf(v1, v2, gamma) for v1 in l1]) for v2 in l1)

	return (1.0/(len(l1)**2)) * sum1 - (1.0/(len(l0)**2))*sum0

agesonly = loadmatch('agesonly.csv', allnum = True)
matchmaker = loadmatch('matchmaker.csv')
avgs = lineartrain(agesonly)
print avgs
print '--- test dp classify---'
print dpclassify([30,30], avgs)
print dpclassify([30,25], avgs)
print dpclassify([25,40], avgs)
print dpclassify([48,20], avgs)

numericalset = loadnumerical()
print numericalset[0].data

print '--- test scale ---'
scaledataset, scalef = scaledata(numericalset)
avgs = lineartrain(scaledataset)
print numericalset[0].data
print numericalset[0].match
print dpclassify(scalef(numericalset[0].data), avgs)
print numericalset[11].match
print dpclassify(scalef(numericalset[11].data), avgs)


print '--- test non linear ---'
offset = getoffset(agesonly)
print nlclassify([30,30], agesonly, offset)
print nlclassify([30,25], agesonly, offset)
print nlclassify([25,40], agesonly, offset)
print nlclassify([48,20], agesonly, offset)

print '--- test non linear after scale ---'
ssoffset = getoffset(scaledataset)
scaledset = scaledataset
print 'original: ', numericalset[0].match
print nlclassify(scalef(numericalset[0].data), scaledset, ssoffset)

print 'original: ', numericalset[1].match
print nlclassify(scalef(numericalset[1].data), scaledset, ssoffset)

print 'original: ', numericalset[2].match
print nlclassify(scalef(numericalset[2].data), scaledset, ssoffset)

# Man doesn't want children, woman does
newrow = [28.9, -1,-1,26.0,-1,1,2,0.8]
print newrow
print nlclassify(scalef(newrow), scaledset, ssoffset)
# Both want children
newrow = [28.0, -1, 1, 26.0, -1,1,2,0.8]
print newrow
print nlclassify(scalef(newrow), scaledset, ssoffset)


