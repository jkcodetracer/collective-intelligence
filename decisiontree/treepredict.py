#!/usr/bin/python

from PIL import Image, ImageDraw

my_data =[['slashdot','USA','yes',18,'None'],
	['google','France','yes',23,'Premium'],
	['digg','USA','yes',24,'Basic'],
	['kiwitobes','France','yes',23,'Basic'],
	['google','UK','no',21,'Premium'],
	['(direct)','New Zealand','no',12,'None'],
	['(direct)','UK','no',21,'Basic'],
	['google','USA','no',24,'Premium'],
	['slashdot','France','yes',19,'None'],
	['digg','USA','no',18,'None'],
	['google','UK','no',18,'None'],
	['kiwitobes','UK','no',19,'None'],
	['digg','New Zealand','yes',12,'Basic'],
	['slashdot','UK','no',21,'None'],
	['google','UK','yes',18,'Basic'],
	['kiwitobes','France','yes',19,'Basic']]

# probability that a randomly placed item will be in the 
# wrong category
def giniimpurity(rows):
	total = len(rows)
	counts = uniquecounts(rows)
	imp = 0
	for k1 in counts:
		p1 = float(counts[k1])/total
		for k2 in counts:
			if k1 == k2:
				continue
			p2 = float(counts[k2])/total
			imp += p1*p2
	return imp


def entropy(rows):
	from math import log
	log2 = lambda x:log(x)/log(2)
	results = uniquecounts(rows)

	ent = 0.0
	for r in results.keys():
		p = float(results[r])/len(rows)
		ent = ent - p*log2(p)
	return ent


# put rows in two sets based on the choosen column
def divideset(rows, column, value):
	split_function = None

	if isinstance(value, int) or isinstance(value, float):
		split_function = lambda row:row[column] >= value
	else:
		split_function = lambda row:row[column] == value
	
	set1 = [row for row in rows if split_function(row)]
	set2 = [row for row in rows if not split_function(row)]
	return (set1, set2)

def uniquecounts(rows):
	results = {}
	for row in rows:
		r = row[len(row)-1]
		if r not in results:
			results[r] = 0
		results[r] += 1

	return results

def buildtree(rows, scoref = entropy):
	if len(rows) == 0:
		return decisionnode()
	current_score = scoref(rows)

	# track the best criteria
	best_gain = 0.0
	best_criteria = None
	best_sets = None

	column_count = len(rows[0]) - 1
	for col in range(0, column_count):
		column_values = {}
		for row in rows:
			column_values[row[col]] = 1

		for value in column_values.keys():
			(set1,set2) = divideset(rows, col, value)

			# information gain
			p = float(len(set1))/len(rows)
			gain = current_score - p*scoref(set1) - (1-p)*scoref(set2)
			if gain > best_gain and len(set1) > 0 and len(set2) > 0:
				best_gain = gain
				best_criteria = (col, value)
				best_sets = (set1, set2)
	# create subbranch 
	if best_gain > 0.0:
		trueBranch = buildtree(best_sets[0])
		falseBranch = buildtree(best_sets[1])
		return decisionnode(col = best_criteria[0], 
				value = best_criteria[1],
				tb = trueBranch, 
				fb = falseBranch)
	else:
		return decisionnode(results = uniquecounts(rows))

def printtree(tree, indent = ''):
	#is leaf node?
	if tree.results != None:
		print str(tree.results)
	else:
		# print the criteria
		print str(tree.col) + ':' + str(tree.value) + '?'

		# print the branches
		print indent + 'T->',
		printtree(tree.tb, indent + ' ')
		print indent + 'F->', 
		printtree(tree.fb, indent + ' ')

def getwidth(tree):
	if tree.tb == None and tree.fb == None:
		return 1
	else:
		return getwidth(tree.tb) + getwidth(tree.fb)

def getdepth(tree):
	if tree.tb == None and tree.fb == None:
		return 1
	else:
		return max(getdepth(tree.fb), getdepth(tree.tb)) + 1

def drawnode(draw, tree, x,y):
	if tree.results == None:
		# get the width of each branch 
		w1 = getwidth(tree.fb)*100
		w2 = getwidth(tree.tb)*100

		# determine the needed space
		left = x-(w1+w2)/2
		right = x+(w1+w2)/2

		draw.text((x-20, y-10), str(tree.col)+':'+str(tree.value),
				(0,0,0))

		draw.line((x,y,left+w1/2,y+100), fill = (255,0,0))
		draw.line((x,y,right-w2/2,y+100), fill = (255,0,0))

		drawnode(draw, tree.fb, left+w1/2, y+100)
		drawnode(draw, tree.tb, right-w2/2, y+100)
	else:
		txt = ' \n'.join(['%s:%d'%v for v in tree.results.items()])
		draw.text((x-20,y), txt, (0,0,0))

def drawtree(tree, jpeg = 'tree.jpg'):
	w = getwidth(tree)*100
	h = getdepth(tree)*100

	img = Image.new('RGB', (w,h), (255,255,255))
	draw = ImageDraw.Draw(img)

	drawnode(draw, tree, w/2, 20)
	img.save(jpeg, 'JPEG')

def classify(observation, tree):
	if tree.results != None:
		return tree.results
	else:
		v = observation[tree.col]
		branch = None

		if isinstance(v, int) or isinstance(v, float):
			if v >= tree.value:
				branch = tree.tb
			else:
				branch = tree.fb
		else:
			if v == tree.value:
				branch = tree.tb
			else:
				branch = tree.fb
	return classify(observation, branch)

class decisionnode:
	def __init__(self, col=-1, value=None, 
			results=None, tb=None, fb=None):
		self.col = col
		self.value = value
		self.results = results
		self.fb = fb
		self.tb = tb

tree = divideset(my_data, 2, 'yes')
print tree[0]
print tree[1]
print '--- gini impurity ---'
print giniimpurity(my_data)
print entropy(my_data)
set1, set2 = divideset(my_data, 2, 'yes')
print entropy(set1)
print giniimpurity(set1)

print '--- test decision tree---'
my_tree = buildtree(my_data)
printtree(my_tree)
drawtree(my_tree)
print classify(['(direct)', 'USA', 'yes', 5], my_tree)

