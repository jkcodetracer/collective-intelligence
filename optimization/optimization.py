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
	d = 0
	while d < len(r):
		print d
		name = people[d/2][0]
		origin = people[d/2][1]
		out = flight[(origin, destination)][r[d]]
		ret = flight[(destination, origin)][r[d+1]]
		print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s |' % \
			(name, origin, out[0], out[1], out[2], \
			ret[0], ret[1], ret[2])
		d += 2

def schedulecost(sol):
	totalprice = 0
	latestarrival = 0
	earliestdep = 24 * 60
	d = 0

	while (d < len(sol)):
		origin = people[d/2][1]
		outbound = flight[(origin, destination)][int(sol[d])]
		returnf = flight[(destination, origin)][int(sol[d+1])]

		totalprice += outbound[2]
		totalprice += returnf[2]

		# Track the latest arrival and earliest departure
		if latestarrival < getminutes(outbound[1]):
			latestarrival = getminutes(outbound[1])

		if earliestdep > getminutes(returnf[0]):
			earliestdep = getminutes(returnf[0])

		d+=2

	# wait for other people
	totalwait = 0
	d = 0
	while (d < len(sol)):
		origin = people[d/2][1]
		outbound = flight[(origin, destination)][int(sol[d])]
		returnf = flight[(destination, origin)][int(sol[d+1])]
		totalwait += latestarrival - getminutes(outbound[1])
		totalwait += getminutes(returnf[0]) - earliestdep
		d += 2

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

def hillclimb(domain, costf):
	#create random solution
	sol = [random.randint(domain[i][0], domain[i][1]) \
		for i in range(len(domain))]

	# main loop
	while 1:
		# create a list of neighbouring solution
		# from two direction
		neighbors = []
		for j in range(len(domain)):
			if sol[j] > domain[j][0]:
				neighbors.append(sol[0:j]+\
					[sol[j]-1]+sol[j+1:])
			if sol[j] < domain[j][1]:
				neighbors.append(sol[0:j]+\
					[sol[j]+1]+sol[j+1:])

		# find the best among neighbors
		current = costf(sol)
		best = current
		for j in range(len(neighbors)):
			cost = costf(neighbors[j])
			if cost < best:
				best = cost
				sol = neighbors[j]
		if best == current:
			break;
	return sol;

def annealingoptimize(domain, costf, T=1000.0, cool=0.98, step=1):
	# Initialize the values randomly
	vec = [random.randint(domain[i][0], domain[i][1]) \
		for i in range(len(domain))]

	while T>0.1:
		i = random.randint(0, len(domain)-1)

		# choose a direction to change it
		dif = random.randint(-step, step)
		# create a new values
		vecb = vec[:]
		vecb[i] += dif
		if vecb[i] < domain[i][0]:
			vecb[i] = domain[i][0]
		elif vecb[i] > domain[i][1]:
			vecb[i] = domain[i][1]

		# compare the cost
		ea = costf(vec)
		eb = costf(vecb)

		# is it better, or make the probability
		if eb < ea:
			vec = vecb
		else:
			# simulated annealing
			p = pow(math.e, -(eb-ea)/T)
			if random.random() < p:
				vec = vecb

		T = T*cool
	return vec

class genetic:
	def __init__(self):
		pass

	def __del__(self):
		pass

	# someone can mutate.
	def mutate(self, vec, domain, step = 1):
		i = random.randint(0, len(domain)-1)
		if random.random() < 0.5:
			step *= -1
		tmp = vec[i] + step

		if tmp < domain[i][0]:
			tmp = domain[i][1]
		elif tmp > domain[i][1]:
			tmp = domain[i][0]

		return vec[0:i]+[tmp]+vec[i+1:]

	# people can breed a new generation
	def crossover(self, r1, r2, domain):
		i = random.randint(1, len(domain)-2)
		return r1[0:i]+r2[i:]

	# the main genetic function
	# popsize: the size of population
	# mutprob: the possiblily of mutation
	# elite: the fraction of the good solution of each generation
	# maxiter: how many generation
	def geneticoptimize(self, domain, costf, popsize = 50, step = 1,\
			mutprob = 0.2, elite = 0.2, maxiter = 100):
		# build the population
		pop = []
		for i in range(popsize):
			vec = [random.randint(domain[j][0], domain[j][1]) \
				for j in range(len(domain))]
			pop.append(vec)

		# how many winners from each generation?
		topelite = int(elite*popsize)

		# optimize the group
		# the max generation is maxiter
		scores = []
		for i in range(maxiter):
			#print pop
			scores = [(costf(v), v) for v in pop]
			scores.sort()
			ranked = [v for (s,v) in scores]

			pop = ranked[0:topelite]
			while len(pop) < popsize:
				if random.random() < mutprob:
					# mutation
					c = random.randint(0, topelite-1)
					pop.append(self.mutate(pop[c], \
						domain, step))
				else:
					# crossover
					c1 = random.randint(0, topelite-1)
					c2 = random.randint(0, topelite-1)
					pop.append(self.crossover(pop[c1],\
						pop[c2], domain))

		scores = [(costf(v), v) for v in pop]
		scores.sort()
		return scores[0][1]


'''
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
printschedule(s)

print '--- test hillclimb ---'
s = hillclimb(domain, schedulecost)
print schedulecost(s)
printschedule(s)


print '--- test simulated annealing ---'
s = annealingoptimize(domain, schedulecost)
print schedulecost(s)
printschedule(s)

print '--- test genetic optmize ---'
gen = genetic()
s = gen.geneticoptimize(domain, schedulecost)
print schedulecost(s)
printschedule(s)
'''

