#!/usr/bin/python

import feedparser
import re
import nmf
import numpy

feedlist = ['http://feeds.bbci.co.uk/news/world/rss.xml',
	'https://news.google.com/news?hl=en&gl=us&q=news&um=1&ie=UTF-8&output=rss',
	'http://feeds.bbci.co.uk/news/rss.xml?edition=int',
	'http://news.yahoo.com/rss/topstories']

# remove all the images and markup in the page.
def stripHTML(h):
	p = ''
	s = 0
	for c in h:
		if c == '<': 
			s = 1
		elif c == '>':
			s = 0
			p += ' '
		elif s == 0:
			p+=c
	return p

def separatewords(text):
	splitter = re.compile('\\W*')
	return [s.lower() for s in splitter.split(text) if len(s) > 3]

def getarticlewords():
	allwords = {}
	articlewords = []
	articletitles = []
	ec = 0

	for feed in feedlist:
		f = feedparser.parse(feed)

		for e in f.entries:
			# ignore identical articles
			if e.title in articletitles:
				continue
			# extract the words
			txt = e.title.encode('utf8')+ \
				stripHTML(e.description.encode('utf8'))
			words = separatewords(txt)
			articlewords.append({})
			articletitles.append(e.title)

			# Increase the counts for this word in allwords and in
			# articlewords
			for word in words:
				allwords.setdefault(word, 0)
				allwords[word] += 1
				articlewords[ec].setdefault(word, 0)
				articlewords[ec][word] += 1
			ec += 1
	return allwords, articlewords, articletitles

def makematrix(allw, articlew):
	wordvec = []

	# take words that are common but not too common
	for w,c in allw.items():
		if c > 3 and c < len(articlew)*0.6:
			wordvec.append(w)

	l1 = [[(word in f and f[word] or 0) for word in wordvec]
		for f in articlew]

	return l1, wordvec

def showfeatures(w,h,titles, wordvec, out = 'features.txt'):
	outfile = file(out, 'w')
	pc,wc = shape(h)
	toppatterns = [[] for i in range(len(titles))]
	patternnames = []

	# loop over all the features
	for i in range(pc):
		slist = []

		for j in range(wc):
			slist.append((h[i,j], wordvec[j]))
		slist.sort()
		slist.reverse()

		n = [s[1] for s in slist[0:6]]
		outfile.write(str(n) + '\n')
		patternnames.append(n)

		flist = []
		for j in range(len(titles)):
			flist.append((w[j,i], titles[j]))
			toppatterns[j].append((w[j,i], i, titles[j]))

		flist.sort()
		flist.reverse()

		for f in flist[0:3]:
			outfile.write(str(f)+'\n')
		outfile.write('\n')
	outfile.close()

	return toppatterns, patternnames


print '--- test word vec---'
allw,artw,artt = getarticlewords()
wordmatrix, wordvec = makematrix(allw, artw)
print wordvec[0:10]
print artt[1]
print wordmatrix[1][0:100]

weights, feat = nmf.factorize(wordmatrix, pc = 20, iter=50)

