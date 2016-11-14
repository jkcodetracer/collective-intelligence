#!/usr/bin/python

import random
import math
import optimization

dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

prefs = [('Toby', ('Bacchus', 'Hercules')),
	 ('Steve', ('Zeus', 'Pluto')),
	 ('Andrea', ('Athena', 'Zeus')),
	 ('Sarah', ('Zeus', 'Pluto')),
	 ('Dave', ('Athena', 'Bacchus')),
	 ('Jeff', ('Hercules', 'Pluto')),
	 ('Fred', ('Pluto', 'Athena')),
	 ('Suzie', ('Bacchus', 'Hercules')),
	 ('Laura', ('Bacchus', 'Hercules')),
	 ('Neil', ('Hercules', 'Athena'))]

domain = [(0,(len(dorms)*2-i-1)) for i in range(0, len(dorms)*2)]

def dormcost(vec):
	cost = 0
	slots = []
	for i in range(len(dorms)):
		slots += [i,i]

	for i in range(len(vec)):
		x = int(vec[i])
		dorm = dorms[slots[x]]
		pref = prefs[i][1]
		if dorm == pref[0]:
			cost += 0
		elif dorm == pref[1]:
			cost += 1
		else:
			cost += 3

		del slots[x]

	return cost


def printsolution(vec):
	slots = []
	for i in range(len(dorms)):
		slots += [i,i]

	for i in range(len(vec)):
		x = int(vec[i])

		dorm = dorms[slots[x]]
		print prefs[i][0], dorm
		del slots[x]

#printsolution([0,0,0,0,0,0,0,0,0,0])

gen_dorm = optimization.genetic()
s = gen_dorm.geneticoptimize(domain, dormcost)
print dormcost(s)
printsolution(s)


