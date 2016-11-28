#!/usr/bin/python

from random import random,randint,choice
from copy import deepcopy
from math import log

# wrap the function nodes
class fwrapper:
	def __init__(self, function, childcount, name):
		self.function = function
		self.childcount = childcount
		self.name = name

# for function node
class node:
	def __init__(self, fw, children):
		self.function = fw.function
		self.name = fw.name
		self.children = children

	def evaluate(self, inp):
		results = [n.evaluate(inp) for n in self.children]
		return self.function(results)

	def display(self, indent = 0):
		print (' '*indent) + self.name
		for c in self.children:
			c.display(indent+1)

# for parameters
class paramnode:
	def __init__(self, idx):
		self.idx = idx

	def evaluate(self, inp):
		return inp[self.idx]

	def display(self, indent = 0):
		print '%sp%d' %(' '*indent, self.idx)

# for constant value
class constnode:
	def __init__(self, v):
		self.v = v

	def evaluate(self, inp):
		return self.v

	def display(self, indent = 0):
		print '%s%d' % (' '*indent, self.v)


addw = fwrapper(lambda l:l[0]+l[1], 2, 'add')
subw = fwrapper(lambda l:l[0]-l[1], 2, 'subtract')
mulw = fwrapper(lambda l:l[0]*l[1], 2, 'multiply')

def iffunc(l):
	if l[0] > 0 :
		return l[1]
	else:
		return l[2]
ifw = fwrapper(iffunc, 3, 'if')

def isgreater(l):
	if l[0] > l[1]:
		return 1
	else:
		return 0

gtw = fwrapper(isgreater, 2, 'isgreater')

flist = [addw, mulw, ifw, gtw, subw]

def makerandomtree(pc, maxdepth = 4, fpr = 0.5, ppr = 0.6):
	if random() < fpr and maxdepth > 0:
		f = choice(flist)
		children = [makerandomtree(pc, maxdepth-1, fpr,ppr) \
				for i in range(f.childcount)]
		return node(f, children)
	elif random() < ppr:
		return paramnode(randint(0, pc-1))
	else:
		return constnode(randint(0, 10))

def hiddenfunction(x,y):
	return x**2 + 2*y + 3*x + 5

def buildhiddenset():
	rows = []
	for i in range(200):
		x = randint(0,40)
		y = randint(0,40)
		rows.append([x,y,hiddenfunction(x,y)])
	return rows

# cost function
def scorefunction(tree, s):
	dif = 0
	for data in s:
		v = tree.evaluate([data[0],data[1]])
		dif += abs(v-data[2])
	return dif

def mutate(t, pc, probchange = 0.1):
	if random() < probchange:
		return makerandomtree(pc)
	else:
		result = deepcopy(t)
		if isinstance(t, node):
			result.children = [mutate(c, pc, probchange) \
				for c in t.children]
		return result

def crossover(t1, t2, probswap = 0.7, top = 1):
	if random() < probswap and not top:
		return deepcopy(t2)
	else:
		result = deepcopy(t1)
		if isinstance(t1, node) and isinstance(t2, node):
			result.children = [crossover(c, choice(t2.children),\
				probswap, 0) for c in t1.children]
		return result

def getrankfunction(dataset):
	def rankfunction(population):
		scores = [(scorefunction(t, dataset), t) for t in population]
		scores.sort()
		return scores
	return rankfunction

def evolve(pc, popsize, rankfunction, maxgen = 500,
	mutationrate = 0.1, breedingrate = 0.4, pexp = 0.7, pnew = 0.05):

	# return a random number, tending towards lower numbers.
	# The lower pexp is, more lower numbers you will get.
	def selectindex():
		return int(log(random())/log(pexp))

	# create a random initial population
	population = [makerandomtree(pc) for i in range(popsize)]
	for i in range(maxgen):
		scores = rankfunction(population)
		print scores[0][0]
		if scores[0][0] == 0:
			break

		newpop = [scores[0][1], scores[1][1]]
		while len(newpop) < popsize:
			if random() > pnew:
				newpop.append(mutate(
					crossover(scores[selectindex()][1],
						scores[selectindex()][1],
						probswap = breedingrate),
					pc, probchange = mutationrate))
			else:
				newpop.append(makerandomtree(pc))
		population = newpop
	scores[0][1].display()
	return scores[0][1]

def gridgame(p):
	max = (3,3)

	# remember the last move for each player
	lastmove = [-1, -1]

	# remember the player's location
	location = [[randint(0, max[0]), randint(0,max[1])]]

	# another player
	location.append([(location[0][0]+2)%4, (location[0][1]+2)%4])
	for o in range(50):

		# for each player
		for i in range(2):
			locs = location[i][:] + location[1-i][:]
			locs.append(lastmove[i])
			move = p[i].evaluate(locs)%4

			# You lose if ou move the same direction twice in a row
			if lastmove[i] == move:
				return 1-i
			lastmove[i] = move
			if move == 0:
				location[i][0]-=1
				if location[i][0] < 0:
					location[i][0] = 0
	 		if move == 1:
				location[i][0] += 1
				if location[i][0] > max[0]:
					location[i][0] = max[0]

			if move == 2:
				location[i][1] -= 1
				if location[i][1] < 0:
					location[i][1] = 0

			if move == 3:
				location[i][1] += 1
				if location[i][1] > max[1]:
					location[i][1] = max[1]

			if location[i] == location[1-i]:
				return i
	return -1

def tournament(pl):
	losses = [0 for p in pl]

	# each player plays with each other
	for i in range(len(pl)):
		for j in range(len(pl)):
			if i == j:
				continue

			winner = gridgame([pl[i], pl[j]])
			if winner == 0:
				losses[j] += 2
			elif winner == 1:
				losses[i] += 2
			elif winner == -1:
				losses[i] += 1
				losses[j] += 1
				pass

	z = zip(losses, pl)
	z.sort()

	return z

# example
def exampletree():
	return node(ifw, [
			node(gtw, [paramnode(0), constnode(3)]),
			node(addw, [paramnode(1), constnode(5)]),
			node(subw, [paramnode(1), constnode(2)]),
			]
		)

print '--- test ---'
examplet = exampletree()
print examplet.evaluate([2,3])
print examplet.evaluate([5,3])
examplet.display()

print '--- test random ---'
random1 = makerandomtree(2)
print random1.evaluate([7,1])
print random1.evaluate([2,4])
random2 = makerandomtree(2)
print random2.evaluate([5,3])
print random2.evaluate([5,20])
print '--- test mutate ---'
muttree = mutate(random2, 2)
muttree.display()
print '--- test cross ---'
cross = crossover(random1, random2)
cross.display()
'''
print '--- test environment ---'
rf = getrankfunction(buildhiddenset())
print evolve(2, 500, rf, mutationrate = 0.2, breedingrate = 0.1, \
		pexp = 0.7, pnew = 0.1)
'''

print '--- test gridgame ---'
p1 = makerandomtree(5)
p2 = makerandomtree(5)
print gridgame([p1,p2])

print '--- grid game evolve---'
winner = evolve(5, 100, tournament, maxgen = 50)
winner.display()


