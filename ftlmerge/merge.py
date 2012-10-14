
from ftlmerge.util import ProfSav
def merge(*profs):
	if len(set([x['version'] for x in profs])) is not 1:
		raise Exception("Incompatible sav files")
	merged = ProfSav()
	merged['version'] = profs[0]['version']

	_mergeAchievements(merged,*profs)
	_mergeShips(merged,*profs)
	merged['highscores'] = dict()
	_mergeHighScores(merged,*profs)
	_mergeShipScores(merged,*profs)
	_mergeOtherScores(merged,*profs)
	_mergeCrew(merged,*profs)
	return merged

def _mergeAchievements(merged,*profs):
	merged['achievements'] = dict();
	merged['achievements']['list'] = list()
	foundSoFar = dict()
	for prof in profs:
		for achievement in prof['achievements']['list']:

			if achievement['name'] in foundSoFar:
				if achievement['difficulty'] == 1:
					foundSoFar[achievement['name']] = achievement
			else:
				foundSoFar[achievement['name']] = achievement
	merged['achievements']['count'] = len(foundSoFar)
	for found in foundSoFar.values():
		merged['achievements']['list'] += [found]

def _mergeShips(merged,*profs):
	merged['ships'] = [0 for x in range(12)]
	for prof in profs:
		for x in range(12):
			if merged['ships'][x] == 1 or prof['ships'][x] == 1:
				merged['ships'][x] = 1
			else:
				merged['ships'][x] = 0

def _mergeHighScores(merged,*profs):
	
	highscoreSet = merged['highscores']['allScore'] = dict()
	highscoreSet['count'] = 5 # must be 5 long
	highscoreSet['keyOrder'] = ['all']
	highscoreSet['instances'] = dict()
	highscoreSet['instances']['all'] = list()
	for profHighScore in [prof['highscores']['allScore']['instances']['all'] for prof in profs]:
		highscoreSet['instances']['all'] += profHighScore

	highscoreSet['instances']['all'] = sorted(
		highscoreSet['instances']['all'], 
		key=lambda a: a['score'],
		reverse=True
	)[:5]

	
def _mergeShipScores(merged,*profs):
	highscoreSet = merged['highscores']['shipScore'] = dict()
	highscoreSet['keyOrder'] = None
	# if the order doesn't need to be maintained this could be MASSIVELY simplified
	for profKeyOrder in [prof['highscores']['shipScore']['keyOrder'] for prof in profs]:
		if highscoreSet['keyOrder'] is None:
			highscoreSet['keyOrder'] = [k for k in profKeyOrder]
		else:
			lastFoundIndex = 0
			for k in profKeyOrder:
				if k  in highscoreSet['keyOrder']:
					lastFoundIndex = highscoreSet['keyOrder'].index(k)
				else:
					highscoreSet['keyOrder'] = \
							highscoreSet['keyOrder'][:lastFoundIndex+1] + \
							[k] + highscoreSet['keyOrder'][lastFoundIndex+1:]
	highscoreSet['keyOrder']
	highscoreSet['instances'] = dict()
	highscoreSet['count'] = 0
	for k in highscoreSet['keyOrder']:
		highscoreSet['instances'][k] = list()
		for prof in profs:
			if k in prof['highscores']['shipScore']['instances']:
				highscoreSet['instances'][k] += prof['highscores']['shipScore']['instances'][k]
		highscoreSet['instances'][k] = sorted(
			highscoreSet['instances'][k], 
			key=lambda a: a['score'],
			reverse=True
		)[:4]
		highscoreSet['count'] += len(highscoreSet['instances'][k]) # might not be 4!
	

def _mergeOtherScores(merged,*profs):
	merged['otherscores'] = dict()
	labels = ['defeated_ships','explored_beacons','scrap','crew','total_games','total_victories']
	for label in labels:
		if label.startswith("total"):
			merged['otherscores'][label] = 0
			merged['otherscores'][label] = sum([ prof['otherscores'][label] for prof in profs])
		else:
			merged['otherscores'][label] = dict()
			mergedLabel = merged['otherscores'][label]
			mergedLabel['best'] = 0
			mergedLabel['total'] = 0
			for prof in profs:
				profLabel = prof['otherscores'][label]
				mergedLabel['best'] = max(profLabel['best'],mergedLabel['best'])
				mergedLabel['total'] += profLabel['total']
	

def _mergeCrew(merged,*profs):
	merged['crew_skills'] = list()
	findTheBest = dict()
	for prof in profs:
		for crewSkill in prof['crew_skills']:
			if crewSkill['skillname'] not in findTheBest:
				findTheBest[crewSkill['skillname']] = crewSkill
			elif findTheBest[crewSkill['skillname']]['score'] < crewSkill['score']:
				findTheBest[crewSkill['skillname']] = crewSkill
	for skillName in ['Repair','Combat Kills','Pilot Evasions', 'Jumps Survived', 'Skill Masteries']:
		merged['crew_skills'] += [findTheBest[skillName]]
	
	