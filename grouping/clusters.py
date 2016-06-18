#!/usr/bin/python

def readfile(filename):
	lines = [line for line in file(filename)]

	# column titles
	colnames = lines[0].strip().split('\t')[1:]
	rownames = []
	data = []

	for line in lines[1:]:
		p = line.strip().split('\t')
		rownames.append(p[0])
		data.append([float(x) for x in p[1:]])

	return rownames, colnames, data

def rotatematrix(data):
	newdata = []
	for i in range(len(data[0])):
		newrow = [data[j][i] for j in range(len(data))]
		newdata.append(newrow)
	return newdata

from math import sqrt

def pearson(v1, v2):
	# simple sums
	sum1 = sum(v1)
	sum2 = sum(v2)

	# sums of the squares
	sum1Sq = sum([ pow(v, 2) for v in v1])
	sum2Sq = sum([ pow(v, 2) for v in v2])

	# sum of the products
	pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

	# calculate r (Pearson score)
	num = pSum - (sum1*sum2/len(v1))
	den = sqrt((sum1Sq - pow(sum1, 2)/len(v1)) * (sum2Sq - \
		pow(sum2, 2)/len(v1)))

	if den == 0:
		return 0

	return 1.0 - num/den


class bicluster:
	def __init__(self, vec, left = None, right = None, \
			distance = 0.0, id = None):
		self.left = left
		self.right = right
		self.vec = vec
		self.id = id
		self.distance = distance


def hcluster(rows, distance = pearson):
	distances = {}
	currentclustid = -1

	# clusters are initially just the rows
	clust = [bicluster(rows[i], id = i) for i in range(len(rows))]

	while len(clust) > 1:
		lowestpair = (0, 1)
		closest = distance(clust[0].vec, clust[1].vec)

		# look for the smallest distance
		for i in range(len(clust)):
			for j in range(i+1, len(clust)):
				if (clust[i].id, clust[j].id) not in distances:
					distances[(clust[i].id, clust[j].id)] = \
					distance(clust[i].vec, clust[j].vec)

				d = distances[(clust[i].id, clust[j].id)]

				if d < closest:
					closest = d
					lowestpair = (i, j)

		# calculate the average of the two cluster
		mergevec = [(clust[lowestpair[0]].vec[i] + \
			     clust[lowestpair[1]].vec[i])/2.0 \
			     for i in range(len(clust[0].vec))]

		# create the father cluster
		newcluster = bicluster(mergevec, left = clust[lowestpair[0]], \
				right = clust[lowestpair[1]], distance = closest,\
				id = currentclustid)

		# clusters that were not in the original set have negetive id.
		currentclustid = -1
		del clust[lowestpair[1]]
		del clust[lowestpair[0]]
		clust.append(newcluster)

	return clust[0]

def getheight(clust):
	if clust.right == None and clust.left == None:
		return 1

	return getheight(clust.left) + getheight(clust.right)

def getdepth(clust):
	if clust.left == None and clust.right == None: 
		return 0

	return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance

# print cluster
def printclust(clust, labels = None, n = 0):
	for i in range(n):
		print ' '
	if clust.id < 0:
		print '-'
	else:
		if labels == None:
			print clust.id
		else:
			print labels[clust.id]

	if clust.left != None:
		printclust(clust.left, labels = labels, n = n+1)
	if clust.right != None:
		printclust(clust.right, labels = labels, n = n+1)

# draw dendrogram 
from PIL import Image, ImageDraw

def drawdendrogram(clust, labels, jpeg = 'clusters.jpeg'):
	# heigth and width
	h = getheight(clust) * 20
	w = 1200
	depth = getdepth(clust)

	# width is fixed , so scaled distance accordingly
	scaling = float(w - 150)/depth

	# create a new image with a white background
	img = Image.new('RGB', (w, h), (255,255,255))
	draw = ImageDraw.Draw(img)

	draw.line((0, h/2, 10, h/2), fill = (255, 0, 0))

	#draw first node
	drawnode(draw, clust, 10, (h/2), scaling, labels)
	img.save(jpeg, 'JPEG')

def drawnode(draw, clust, x, y, scaling, labels):
	if clust.id >= 0:
		draw.text((x+5, y-7), labels[clust.id], (0, 0, 0))
	else:
		h1 = getheight(clust.left) * 20
		h2 = getheight(clust.right) * 20
		top = y - (h1 + h2)/2
		bottom = y + (h1 + h2)/2

		ll = clust.distance * scaling
		draw.line((x, top + h1/2, x, bottom - h2/2), fill=(255,0,0))
		draw.line((x, top+h1/2, x+ll, top + h1/2), fill=(255,0,0))
		draw.line((x, bottom-h2/2, x+ll, bottom-h2/2), fill=(255,0,0))
		
		drawnode(draw, clust.left, x+ll, top + h1/2, scaling, labels)
		drawnode(draw, clust.right, x+ll, bottom - h2/2, scaling, labels)
	

# test
blognames, words, data = readfile('blogdata.txt')
clust = hcluster(data)

printclust(clust, blognames)

drawdendrogram(clust, blognames, jpeg = 'blogclust.jpeg')

# from column view
blognames, words, data = readfile('blogdata.txt')
transdata = rotatematrix(data)
newclust = hcluster(transdata)
drawdendrogram(newclust, labels = words, jpeg = 'wordsclust.jpeg')

