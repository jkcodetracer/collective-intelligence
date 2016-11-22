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

class naivebayes(classifier):
	def __init__(self, getfeatures):
		classifier.__init__(self, getfeatures)
		self.thresholds= {}

	def setthreshold(self, cat, t):
		self.thresholds[cat] = t

	def getthreshold(self, cat):
		if cat not in self.thresholds:
			return 1.0
		return self.thresholds[cat]

	def classify(self, item, default = None):
		probs = {}
		# find the category with the highest probability
		max = 0.0
		for cat in self.categories():
			probs[cat] = self.prob(item, cat)
			if probs[cat] > max:
				max = probs[cat]
				best = cat
		# make sure the probability exceed threshold*next
		for cat in probs:
			if cat == best:
				continue
			if probs[cat]*self.getthreshold(best)>probs[best]:
				return default
		return best

	# calculate the P(category|document)
	# p(category|document) = 
	#	P(document|category) * P(category)/P(document)
	# we can ignore the P(document), because all the documents 
	# have the same possilibity.
	def prob(self, item, cat):
		catprob = self.catcount(cat)/self.totalcount()
		docprob = self.docprob(item, cat)
		return docprob * catprob

	# P(document|category) = P(wordA|category)*P(wordB|category)...
	def docprob(self, item, cat):
		features = self.getfeatures(item)

		p = 1
		for f in features:
			# P(wordX|caeory)
			p *= self.weightedprob(f, cat, self.fprob)
		return p

class fisherclassifier(classifier):
	# P(category|feature) 
	def cprob(self, f, cat):
		# the frequency of this feature in this category
		# P(feature|category)
		clf = self.fprob(f, cat)
		if clf == 0:
			return 0

		# The frequency of this feature in all the categories
		# sum(P(feature|category A), P(feature|category B)...)
		freqsum = sum([self.fprob(f,c) for c in self.categories()])

		# The probability is the frequency in this category divided 
		# by the overall frequency
		# P = P(feature|category)/sum(P(feature|category A), P(B)...)
		p = clf/(freqsum)

		return p

	def invchi2(self, chi, df):
		m = chi/2.0
		sum = term = math.exp(-m)
		for i in range(1, df//2):
			term *= m/i
			sum += term
		return min(sum, 1.0)

	def fisherprob(self, item, cat):
		# multiply all the probabilities together
		p = 1
		features = self.getfeatures(item)
		for f in features:
			p *= self.weightedprob(f,cat,self.cprob)

		# take the natural log and multiply by -2
		fscore = -2*math.log(p)

		# use the inverse chi2 function to get a probability
		return self.invchi2(fscore, len(features)*2)


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

print '--- test naivebayes ---'
nb = naivebayes(getwords)
sampletrain(nb)
print nb.prob('quick rabbit', 'good')
print nb.prob('quick rabbit', 'bad')
print nb.classify('quick rabbit', default='unknown')
print nb.classify('quick money', default='unknown')
nb.setthreshold('bad', 3.0)
print nb.classify('quick money', default='unknown')
for i in range(10):
	sampletrain(nb)
print nb.classify('quick money', default = 'unknown')


print '--- test fisher method ---'
fi = fisherclassifier(getwords)
sampletrain(fi)
print fi.cprob('quick', 'good')
print fi.cprob('money', 'bad')
print fi.weightedprob('money', 'bad', fi.cprob)
print fi.fisherprob('quick rabbit', 'good')
print fi.fisherprob('quick rabbit', 'bad')



