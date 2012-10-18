import struct
import binascii
import os

def read_int(binaryFile):
    return struct.unpack("<I", binaryFile.read(4))[0]

def read_string(binaryFile, l):
    return bytes(binaryFile.read(l))

def write_int(binaryFile, i):
    data = struct.pack("<I", i) # little endian 32 bit.
    binaryFile.write(data)

def write_string(binaryFile, s):
    l = struct.pack("<I",len(s)) # little endian 32 bit.
    binaryFile.write(l)
    # print struct.pack("s",s)
    binaryFile.write(s)

class ProfSav(object):

    def __init__(self, filename=None):
        self.out = {}
        if filename is not None:
            print('Reading: %s' % filename)
            self.read(filename)

    def __getitem__(self, k):
        return self.out[k]

    def __setitem__(self, k, v):
        self.out[k] = v

    def __str__(self):
        return str(self.out)

    def write(self, loc):
        try:
            f = open(loc, "w+b")
        except:
            print('Could not open %s to write the result' % loc)
            exit(-1)
        write_int(f, self.out['version'])
        write_int(f, self.out['achievements']['count'])
        for achievement in self.out['achievements']['list']:
            write_string(f, achievement['name'])
            write_int(f, achievement['difficulty'])

        for ship in self.out['ships']:
            write_int(f,ship)

        # # Begin high scores (repeated twice)
        for highscore_set_name in ["allScore","shipScore"]: #wtf?
            highscore_set = self.out['highscores'][highscore_set_name]
            write_int(f, highscore_set['count'])
            for highscoreKey in highscore_set['keyOrder']:
                highscoreDict = highscore_set['instances'][highscoreKey]
                for highscore in highscoreDict:
                    write_string(f, highscore['name'])
                    write_string(f, highscore['type'])
                    write_int(f, highscore['score'])
                    write_int(f, highscore['sector'])
                    write_int(f, highscore['victory'])
                    write_int(f, highscore['difficulty'])
        # # End high score repeats

        write_int(f, self.out['otherscores']['defeated_ships']['best'])
        write_int(f, self.out['otherscores']['defeated_ships']['total'])
        write_int(f, self.out['otherscores']['explored_beacons']['best'])
        write_int(f, self.out['otherscores']['explored_beacons']['total'])
        write_int(f, self.out['otherscores']['scrap']['best'])
        write_int(f, self.out['otherscores']['scrap']['total'])
        write_int(f, self.out['otherscores']['crew']['best'])
        write_int(f, self.out['otherscores']['crew']['total'])
        write_int(f, self.out['otherscores']['total_games'])
        write_int(f, self.out['otherscores']['total_victories'])

        for skill in self.out['crew_skills']:
            # 4 bytes (32bit int)        Skill Score (e.g. repairs, kills, etc.)
            # 4 bytes (32bit int)        String Length (Crew member name)
            # n bytes (string)           Crew member name
            # 4 bytes (32bit int)        String Length (Crew member race)
            # n bytes (string)           Crew member race (short version, e.g. "engi")
            # 4 bytes (32bit int)        Gender (1 = Male) 
            write_int(f, skill['score'])
            write_string(f, skill['name'])
            write_string(f, skill['race'])
            write_int(f, skill['gender'])


    def read(self,loc):
        try:
            f = open(loc, "rb")
        except:
            print('Could not open %s for reading' % loc)
            exit(-1)
        # Header
        # 4 bytes (32bit int)        Version
        self.out['version'] = read_int(f)

        # # Achievements
        # 4 bytes (32bit int)        Number of achievements
        nAchievements = read_int(f)
        self.out['achievements'] = {
                'count': nAchievements,
                'list': []
            }
        #  # Begin achievement unlock (repeated for each achievement unlocked -- 'Number of achievements')
        #  4 bytes (32bit int)        String Length (Achievement name)
        #  n bytes (char *)           Achievement name
        #  4 bytes (32bit int)        Unknown (seems to be 0/1 a lot though ...)
        #  # End achievement unlock
        for _ in range(nAchievements):
            achievement = {
                    'name': read_string(f, read_int(f)),
                    'difficulty': read_int(f),
                }
            self.out['achievements']['list'].append(achievement)

        # # Repeated 12 times at present, indicating ship unlocks
        # 4 bytes (32bit int)        Ship unlock (as binary)
        self.out['ships'] = []
        for _ in range(12):
            self.out['ships'].append(read_int(f))

        self.out['highscores'] = {}
        # # Begin high scores (repeated twice)
        for set_name in ['allScore','shipScore']: #wtf?
            # 4 bytes (32bit int)        Number of high scores in this set
            nHighScores = read_int(f)
            highscore_set = {
                    'count': nHighScores,
                    'keyOrder': [],
                    'instances':  {}
                }
            self.out['highscores'][set_name] = highscore_set

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
            for _ in range(nHighScores):
                highscore = {
                        'name': read_string(f, read_int(f)),
                        'type': read_string(f, read_int(f)),
                        'score': read_int(f),
                        'sector': read_int(f),
                        'victory': read_int(f),
                        'difficulty': read_int(f),
                    }
                instance_name = highscore['name']

                if set_name == "allScore":
                    instance_name = "all"
                if not instance_name in highscore_set['keyOrder']:
                    highscore_set['keyOrder'].append(instance_name)
                if not instance_name in highscore_set['instances']:
                    highscore_set['instances'][instance_name] = []
                highscore_set['instances'][instance_name].append(highscore)
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
        self.out['otherscores'] = {
                'defeated_ships': {
                    'best': read_int(f),
                    'total': read_int(f),
                    },
                'explored_beacons': {
                    'best': read_int(f),
                    'total': read_int(f),
                    },
                'scrap': {
                    'best': read_int(f),
                    'total': read_int(f),
                    },
                'crew': {
                    'best': read_int(f),
                    'total': read_int(f),
                    },
                'total_games': read_int(f),
                'total_victories': read_int(f),
            }

        # # Repeated five times for Repair, Combat Kills, Pilot Evasions, Jumps Survived, Skill Masteries
        self.out['crew_skills'] = []
        for skillName in ['Repair','Combat Kills','Pilot Evasions', 'Jumps Survived', 'Skill Masteries']:
            # 4 bytes (32bit int)        Skill Score (e.g. repairs, kills, etc.)
            # 4 bytes (32bit int)        String Length (Crew member name)
            # n bytes (string)           Crew member name
            # 4 bytes (32bit int)        String Length (Crew member race)
            # n bytes (string)           Crew member race (short version, e.g. "engi")
            # 4 bytes (32bit int)        Gender (1 = Male) 
            skill = {
                    'skillname': skillName,
                    'score': read_int(f),
                    'name': read_string(f, read_int(f)),
                    'race': read_string(f, read_int(f)),
                    'gender': read_int(f),
                }
            self.out['crew_skills'].append(skill)

