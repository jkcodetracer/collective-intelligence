#!/usr/bin/python

import re
import math

def getwords(doc):
	splitter = re.compile('\\W*')

	words = [s.lower() for s in splitter.split(doc) \
			if len(s) > 2 and len(s) < 20 ]

	return dict([(w,1) for w in words])

def sampletrain(cl):
	cl.train('Nobody owns the water.', 'good')
	cl.train('the quick rabbit jumps fences', 'good')
	cl.train('buy pharmaceuticals now', 'bad')
	cl.train('make quick money at the online casino', 'bad')
	cl.train('the quick brown fox jumps', 'good')

class classifier:
	def __init__(self, getfeatures, filename = None):
		# counts of feature/category combinations
		self.fc = {}
		# counts of documents in each category
		self.cc = {}
		self.getfeatures = getfeatures

	# increase the count of a feature/category pair
	def incf(self, f, cat):
		self.fc.setdefault(f, {})
		self.fc[f].setdefault(cat, 0)
		self.fc[f][cat] += 1

	# increase the count of a category
	def incc(self, cat):
		self.cc.setdefault(cat, 0)
		self.cc[cat] += 1

	# the number of times a feature has appeared in a category
	def fcount(self, f, cat):
		if f in self.fc and cat in self.fc[f]:
			return float(self.fc[f][cat])
		return 0.0

	# The number of items in a category
	def catcount(self, cat):
		if cat in self.cc:
			return float(self.cc[cat])
		return 0

	# the total number of items
	def totalcount(self):
		return sum(self.cc.values())

	# the list of all categories
	def categories(self):
		return self.cc.keys()

	def train(self, item, cat):
		features = self.getfeatures(item)
		for f in features:
			self.incf(f, cat)

		self.incc(cat)

	# return the possibility of f->cat
	# P(A|B) == P(word|classification)
	# the probability of A given B
	def fprob(self, f, cat):
		if self.catcount(cat) == 0:
			return 0
		return self.fcount(f, cat)/self.catcount(cat)

	# if samples are very rare, we'd better use 
	# assumed probability to allivieate the probability
	def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
		# calculate current probability
		basicprob = prf(f, cat)

		# count the number of times this features has appeared in
		# all categories
		totals = sum([self.fcount(f,c) for c in self.categories()])

		# calculate the weighted average
		bp = ((weight*ap) + (totals*basicprob))/(weight+totals)
		return bp


# test simple word
cl = classifier(getwords)
cl.train('the Quick brown fox jumps over the lazy dog', 'good')
cl.train('make quick money in the online casino', 'bad')
print cl.fcount('quick', 'good')
print cl.fcount('quick', 'bad')

sampletrain(cl)
print cl.fprob('quick', 'good')
print cl.weightedprob('money', 'good', cl.fprob)
sampletrain(cl)
print cl.weightedprob('money', 'good', cl.fprob)

