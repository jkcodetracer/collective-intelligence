#!/usr/bin/python

import feedparser
import re

# return title and dictionary of word counts for an RSS feed
def getwordcounts(url):
	#parse the feed 
	d = feedparser.parse(url)
	wc = {}

	# loop over all the entries
	for e in d.entries:
		if 'summary' in e:
			summary = e.summary
		else:
			summary = e.description

		words = getwords(e.title+' '+ summary)
		for word in words:
			wc.setdefault(word, 0)
			wc[word] += 1

	return d.feed.title, wc

# word count
def getwords(html):
	# remove the html tags
	txt = re.compile(r'<[^>]>').sub('', html)

	# split words 
	words = re.compile(r'[^A-Z^a-z]+').split(txt)

	#covert to lowercase
	return [word.lower() for word in words if word != '']

# do the count
apcount = {}
wordcounts = {}
feedlistlen = 0

for feedurl in file('feedlist.txt'):
	print feedurl
	feedlistlen += 1
	title, wc = getwordcounts(feedurl)
	wordcounts[title] = wc
	for word, count in wc.items():
		apcount.setdefault(word, 0)
		if count > 1:
			apcount[word]+=1
# remove normal and unusual word
wordlist = []
for w, bc in apcount.items():
	frac = float(bc)/feedlistlen
	if frac > 0.1 and frac < 0.5 : 
		wordlist.append(w)

out = file('blogdata.txt', 'w')
out.write('Blog')
for word in wordlist:
	out.write('\t%s' % word)
out.write('\n')

for blog, wc in wordcounts.items():
	out.write(blog)
	for word in wordlist:
		if word in wc:
			out.write('\t%d' % wc[word])
		else:
			out.write('\t0')
	out.write('\n')


