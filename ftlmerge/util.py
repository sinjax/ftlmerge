import struct
import binascii
def readInt(binaryFile):
	return struct.unpack("<I",binaryFile.read(4))[0]

def readString(binaryFile,l):
	return str(binaryFile.read(l))

def writeInt(binaryFile,i):
	data = struct.pack("<I",i) # little endian 32 bit.
	binaryFile.write(data)

def writeString(binaryFile,s):
	l = struct.pack("<I",len(s)) # little endian 32 bit.
	binaryFile.write(l)
	# print struct.pack("s",s)
	binaryFile.write(s)

class ProfSav(object):
	def __init__(self,filename=None):
		super(ProfSav, self).__init__()
		self.out = dict()
		if filename is not None:
			self.read(filename)

	def __getitem__(self,k):
		return self.out[k]
	def __setitem__(self,k,v):
		self.out[k] = v
	def __str__(self):
		return str(self.out)

	def write(self,loc):
		f = open(loc,"w+b")
		writeInt(f,self.out['version'])
		writeInt(f,self.out['achievements']['count'])
		for achievment in self.out['achievements']['list']:
			writeString(f,achievment['name'])
			writeInt(f,achievment['difficulty'])

		for ship in self.out['ships']:
			writeInt(f,ship)

		# # Begin high scores (repeated twice)
		for highscoreSetName in ["allScore","shipScore"]: #wtf?
			highscoreSet = self.out['highscores'][highscoreSetName]
			writeInt(f,highscoreSet['count'])
			for highscoreKey in highscoreSet['keyOrder']:
				highscoreDict = highscoreSet['instances'][highscoreKey]
				for highscore in highscoreDict:
					writeString(f,highscore['name'])
					writeString(f,highscore['type'])
					writeInt(f,highscore['score'])
					writeInt(f,highscore['sector'])
					writeInt(f,highscore['victory'])
					writeInt(f,highscore['difficulty'])
		# # End high score repeats

		writeInt(f,self.out['otherscores']['defeated_ships']['best'])
		writeInt(f,self.out['otherscores']['defeated_ships']['total'])
		writeInt(f,self.out['otherscores']['explored_beacons']['best'])
		writeInt(f,self.out['otherscores']['explored_beacons']['total'])
		writeInt(f,self.out['otherscores']['scrap']['best'])
		writeInt(f,self.out['otherscores']['scrap']['total'])
		writeInt(f,self.out['otherscores']['crew']['best'])
		writeInt(f,self.out['otherscores']['crew']['total'])
		writeInt(f,self.out['otherscores']['total_games'])
		writeInt(f,self.out['otherscores']['total_victories'])

		for skill in self.out['crew_skills']:
			# 4 bytes (32bit int)        Skill Score (e.g. repairs, kills, etc.)
			# 4 bytes (32bit int)        String Length (Crew member name)
			# n bytes (string)           Crew member name
			# 4 bytes (32bit int)        String Length (Crew member race)
			# n bytes (string)           Crew member race (short version, e.g. "engi")
			# 4 bytes (32bit int)        Gender (1 = Male) 
			writeInt(f,skill['score'])
			writeString(f,skill['name'])
			writeString(f,skill['race'])
			writeInt(f,skill['gender'])


	def read(self,loc):
		f = open(loc,"rb")
		# Header
		# 4 bytes (32bit int)        Version
		self.out['version'] = readInt(f)
		
		# # Achievements
		# 4 bytes (32bit int)        Number of achievements
		nAchievements = readInt(f)
		self.out['achievements'] = dict()
		self.out['achievements']['count'] = nAchievements
		self.out['achievements']['list'] = list()
		#  # Begin achievement unlock (repeated for each achievement unlocked -- 'Number of achievements')
		#  4 bytes (32bit int)        String Length (Achievement name)
		#  n bytes (char *)           Achievement name
		#  4 bytes (32bit int)        Unknown (seems to be 0/1 a lot though ...)
		#  # End achievement unlock
		for x in xrange(nAchievements):
			achievement = dict()
			self.out['achievements']['list'] += [achievement]
			achievement['name'] = readString(f,readInt(f))
			achievement['difficulty'] = readInt(f)
		
		# # Repeated 12 times at present, indicating ship unlocks
		# 4 bytes (32bit int)        Ship unlock (as binary)
		self.out['ships'] = list()
		for x in xrange(12):
			self.out['ships'] += [readInt(f)]
		
		self.out['highscores'] = dict()
		# # Begin high scores (repeated twice)
		for setName in ['allScore','shipScore']: #wtf?
			# 4 bytes (32bit int)        Number of high scores in this set
			nHighScores = readInt(f)
			highscoreSet = dict()
			self.out['highscores'][setName] = highscoreSet
			highscoreSet['count'] = nHighScores
			highscoreSet['keyOrder'] = list()
			highscoreSet['instances'] = dict()
			
			#   # Begin individual 'top score' (repeated once for each high score in this set)
			#   4 bytes (32bit int)    String Length (Ship name)
			#   n bytes (string)       Ship name
			#   4 bytes (32bit int)    String Length (Ship Type)
			#   n bytes (string)       Ship Type
			#   4 bytes (32bit int)    Score
			#   4 bytes (32bit int)    Sector (e.g. 8 = Sector 8)
			#   4 bytes (32bit int)    Victory (1 = true; 0 = false)
			#   4 bytes (32bit int)    Difficulty (1 = easy; 0 = normal)
			#   # End individual top score
			for y in xrange(nHighScores):
				highscore = dict();
				instanceName = highscore['name'] = readString(f,readInt(f))
				highscore['type'] = readString(f,readInt(f))
				highscore['score'] = readInt(f)
				highscore['sector'] = readInt(f)
				highscore['victory'] = readInt(f)
				highscore['difficulty'] = readInt(f)

				if setName is "allScore":
					instanceName = "all"
				if not instanceName in highscoreSet['keyOrder']:
					highscoreSet['keyOrder'] += [instanceName]
				if not instanceName in highscoreSet['instances']:
					highscoreSet['instances'][instanceName] = list()
				highscoreSet['instances'][instanceName] += [highscore]
		# # End high score repeats
		
		# # General/running scores
		# 4 bytes (32bit int)        Best ships defeated in a session
		# 4 bytes (32bit int)        Total ships defeated (all sessions)
		# 4 bytes (32bit int)        Best beacons explored in a session
		# 4 bytes (32bit int)        Total beacons explored (all sessions)
		# 4 bytes (32bit int)        Best scrap collected in a session
		# 4 bytes (32bit int)        Total scrap collected (all sessions)
		# 4 bytes (32bit int)        Most number of crew hired in a session
		# 4 bytes (32bit int)        Total number of crew hired (all sessions)
		# 4 bytes (32bit int)        Total games played
		# 4 bytes (32bit int)        Total number of victories
		self.out['otherscores'] = dict()
		self.out['otherscores']['defeated_ships'] = dict()
		self.out['otherscores']['explored_beacons'] = dict()
		self.out['otherscores']['scrap'] = dict()
		self.out['otherscores']['crew'] = dict()
		self.out['otherscores']['defeated_ships']['best'] = readInt(f)
		self.out['otherscores']['defeated_ships']['total'] = readInt(f)
		self.out['otherscores']['explored_beacons']['best'] = readInt(f)
		self.out['otherscores']['explored_beacons']['total'] = readInt(f)
		self.out['otherscores']['scrap']['best'] = readInt(f)
		self.out['otherscores']['scrap']['total'] = readInt(f)
		self.out['otherscores']['crew']['best'] = readInt(f)
		self.out['otherscores']['crew']['total'] = readInt(f)
		self.out['otherscores']['total_games'] = readInt(f)
		self.out['otherscores']['total_victories'] = readInt(f)
		
		# # Repeated five times for Repair, Combat Kills, Pilot Evasions, Jumps Survived, Skill Masteries
		self.out['crew_skills'] = list()
		for skillName in ['Repair','Combat Kills','Pilot Evasions', 'Jumps Survived', 'Skill Masteries']:
			# 4 bytes (32bit int)        Skill Score (e.g. repairs, kills, etc.)
			# 4 bytes (32bit int)        String Length (Crew member name)
			# n bytes (string)           Crew member name
			# 4 bytes (32bit int)        String Length (Crew member race)
			# n bytes (string)           Crew member race (short version, e.g. "engi")
			# 4 bytes (32bit int)        Gender (1 = Male) 
			skill = dict()
			self.out['crew_skills'] += [skill]
			skill['skillname'] = skillName
			skill['score'] = readInt(f)
			skill['name'] = readString(f,readInt(f))
			skill['race'] = readString(f,readInt(f))
			skill['gender'] = readInt(f)
		