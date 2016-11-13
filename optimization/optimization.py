#!/usr/bin/python

import time
import random
import math

people = [('Seymour', 'BOS'),
	  ('Franny', 'DAL'),
	  ('Zooey', 'CAK'),
	  ('Walt', 'MIA'),
	  ('Buddy', 'ORD'),
	  ('Les', 'OMA')]

destination = 'LGA'


def getminutes(t):
	x = time.strptime(t, '%H:%M')
	return x[3]*60 + x[4]

def printschedule(r):
	bd = len(r)/2
	for d in range(len(r)/2):
		print '%d %d' % (d, d+bd)
		name = people[d][0]
		origin = people[d][1]
		out = flight[(origin, destination)][r[d]]
		ret = flight[(destination, origin)][r[d+bd]]
		print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % \
			(name, origin, out[0], out[1], out[2], \
			ret[0], ret[1], ret[2])

def schedulecost(sol):
	totalprice = 0
	latestarrival = 0
	earliestdep = 24 * 60
	bd = len(sol)/2

	for d in range(len(sol)/2):
		origin = people[d][1]
		outbound = flight[(origin, destination)][int(sol[d])]
		returnf = flight[(destination, origin)][int(sol[d+bd])]

		totalprice += outbound[2]
		totalprice += returnf[2]

		# Track the latest arrival and earliest departure
		if latestarrival < getminutes(outbound[1]):
			latestarrival = getminutes(outbound[1])

		if earliestdep > getminutes(returnf[0]):
			earliestdep = getminutes(returnf[0])

	# wait for other people
	totalwait = 0
	for d in range(len(sol)/2):
		origin = people[d][1]
		outbound = flight[(origin, destination)][int(sol[d])]
		returnf = flight[(destination, origin)][int(sol[d+bd])]
		totalwait += latestarrival - getminutes(outbound[1])
		totalwait += getminutes(returnf[0]) - earliestdep

	if latestarrival > earliestdep:
		totalprice += 50

	return totalprice + totalwait

def randomoptimize(domain, costf):
	best = 999999999
	bestr = None

	for i in range(1000):
		# a random solution...
		r = [random.randint(domain[i][0], domain[i][1]) \
			for i in range(len(domain))]
		cost = costf(r)

		# update the best
		if cost < best:
			best = cost
			bestr = r

	return r


flight = {}
for line in file('schedule.txt'):
	origin,dest,depart,arrive,price = line.strip().split(',')
	flight.setdefault((origin,dest), [])

	flight[(origin,dest)].append((depart, arrive, int(price)))

s = [1,4,3,2,7,3,6,3,2,4,5,3]
printschedule(s)
print schedulecost(s)

domain = [(0,8)]*(len(people)*2)
s = randomoptimize(domain, schedulecost)
print '--- test random ---'
print schedulecost(s)
print printschedule(s)



