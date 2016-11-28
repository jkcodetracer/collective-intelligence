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


