# A dictionary of movie critics and their ratings of a small
# set of movies

from math import sqrt

critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,      'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,      'The Night Listener': 3.0},     'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,      'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,      'You, Me and Dupree': 3.5},     'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,      'Superman Returns': 3.5, 'The Night Listener': 4.0},     'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,      'The Night Listener': 4.5, 'Superman Returns': 4.0,      'You, Me and Dupree': 2.5},     'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,      'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,      'You, Me and Dupree': 2.0},     'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,      'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},     'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

# distance-based similarity score
def sim_distance(prefs, person1, person2):
	#get the list of shared_items
	si = {}
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item] = 1

	# if they have no ratings in common, return 0
	if len(si) == 0: return 0

	# Add up the squares of all the differences
	sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
				for item in prefs[person1] if item in prefs[person2]])

	return 1/(1 + sum_of_squares)

print sim_distance(critics, 'Lisa Rose', 'Gene Seymour')

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2]: si[item] = 1

	n = len(si)
	if n == 0: return 0
	# add up all the preferences
	sum1 = sum([prefs[p1][it] for it in si])
	sum2 = sum([prefs[p2][it] for it in si])

	# Sum up the squares
	sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
	sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
	
	# sum up the products
	pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

	# caldulate Pearson score
	num = pSum - (sum1*sum2/n)
	den = sqrt((sum1Sq - pow(sum1, 2)/n)*(sum2Sq - pow(sum2, 2)/n))
	if den == 0:
		return 0
	r = num/den

	return r

print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')

# return the best matches for person from the prefs dictionary
def topMatches(prefs, person, n = 5, similarity = sim_pearson):
	scores = [(similarity(prefs, person, other), other) 
			for other in prefs if other != person]
	scores.sort()
	scores.reverse()
	return scores[0:n]

print topMatches(critics, 'Toby', n = 3)

# Gets recommendations for a person by useing a weighted average
# of every other user's rankings
def getRecommendations(prefs, person, similarity = sim_pearson):
	totals = {}
	simSums = {}
	for other in prefs:
		# not myself
		if other == person: continue
		sim = similarity(prefs, person, other)

		# ignore scores of zero or lower
		if sim <= 0: continue
		for item in prefs[other]:
			# sorce the movie I haven't seen
			if item not in prefs[person] or \
				prefs[person][item] == 0:
				totals.setdefault(item, 0)
				totals[item] += prefs[other][item] * sim;
				# sum of similarities
				simSums.setdefault(item, 0)
				simSums[item] += sim
	#Create the normalized list
	rankings = [(total/simSums[item], item) for item, total in
			totals.items()]
	rankings.sort()
	rankings.reverse()
	return rankings

print getRecommendations(critics, 'Toby')
print getRecommendations(critics, 'Toby', similarity = sim_distance)


# transfer
def transformPrefs(prefs):
	result = {}
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item, {})
			result[item][person] = prefs[person][item]

	return result

def calculateSimilarItems(prefs, n = 10):
	result = {}

	itemPrefs = transformPrefs(prefs)
	for item in itemPrefs:
		scores = topMatches(itemPrefs, item, n = n, \
				similarity = sim_distance)
		result[item] = scores

	return result

# items-based recommend
# 根据已有的评分，估算没有被评分的物品的分数
def getRecommendedItems(prefs, itemMatch, user):
	userRatings = prefs[user]
	scores = {}
	totalSim = {}

	for (item, rating) in userRatings.items():
		for (similarity, items2) in itemMatch[item]:
			if items2 in userRatings: continue

			scores.setdefault(items2, 0)
			scores[items2] += similarity * rating

			totalSim.setdefault(items2, 0)
			totalSim[items2] += similarity
	rankings = [(score/totalSim[item], item) for item, score in \
			scores.items()]
	rankings.sort()
	rankings.reverse()

	return rankings




