from ftlmerge.util import ProfSav

def merge(profs):
    """
    Merge the list of savefiles provided into one ProfSav object
    """
    if len(set([x['version'] for x in profs])) != 1:
        raise Exception("Incompatible sav files")
    merged = ProfSav()
    merged['version'] = profs[0]['version']

    merged['achievements'] = merge_achievements(profs)
    merged['ships'] = merge_ships(profs)
    merged['highscores'] = {
            'allScore': merge_highscores(profs),
            'shipScore': merge_ship_scores(profs),
        }
    merged['otherscores'] = merge_other_scores(profs)
    merged['crew_skills'] = merge_crew(profs)
    return merged

def merge_achievements(profs):
    """
    Merge the achievements and keep the highest difficulty
    """
    achievements = {}
    achievements['list'] = []
    found = {}
    for prof in profs:
        for achievement in prof['achievements']['list']:
            if achievement['name'] in found:
                if achievement['difficulty'] == 1:
                    found[achievement['name']] = achievement
            else:
                found[achievement['name']] = achievement
    achievements['count'] = len(found)
    for found_item in found.values():
        achievements['list'].append(found_item)
    return achievements

def merge_ships(profs):
    """
    Merge the available ships
    """
    ships = [0 for x in range(12)]
    for prof in profs:
        for x in range(12):
            if 1 in (ships[x], prof['ships'][x]):
                ships[x] = 1
            else:
                ships[x] = 0
    return ships

def merge_highscores(profs):
    """
    Merge the highscores into one dict
    """
    highscore_set = {
            'count': 5, # must be 5 long
            'keyOrder': ['all'],
            'instances': {
                'all': [],
            },
        }

    for profHighScore in [prof['highscores']['allScore']['instances']['all'] for prof in profs]:
        highscore_set['instances']['all'] += profHighScore

    highscore_set['instances']['all'] = sorted(
            highscore_set['instances']['all'],
            key=lambda a: a['score'],
            reverse=True
        )[:5]
    return highscore_set

def merge_ship_scores(profs):
    """
    Merge ship scores
    """
    highscore_set = {
            'keyOrder': None,
            'instances': {},
            'count': 0
        }
    # if the order doesn't need to be maintained this could be MASSIVELY simplified
    for profKeyOrder in [prof['highscores']['shipScore']['keyOrder'] for prof in profs]:
        if highscore_set['keyOrder'] is None:
            highscore_set['keyOrder'] = [k for k in profKeyOrder]
        else:
            lastFoundIndex = 0
            for k in profKeyOrder:
                if k in highscore_set['keyOrder']:
                    lastFoundIndex = highscore_set['keyOrder'].index(k)
                else:
                    highscore_set['keyOrder'] = (
                            highscore_set['keyOrder'][:lastFoundIndex+1] +
                            [k] + highscore_set['keyOrder'][lastFoundIndex+1:]
                        )
    for k in highscore_set['keyOrder']:
        highscore_set['instances'][k] = []
        for prof in profs:
            if k in prof['highscores']['shipScore']['instances']:
                highscore_set['instances'][k] += prof['highscores']['shipScore']['instances'][k]
        highscore_set['instances'][k] = sorted(
                highscore_set['instances'][k],
                key=lambda a: a['score'],
                reverse=True
            )[:4]
        highscore_set['count'] += len(highscore_set['instances'][k]) # might not be 4!
    return highscore_set


def merge_other_scores(profs):
    """
    Merge all the other scores into one dict
    """
    other_scores = {}
    labels = ['defeated_ships','explored_beacons','scrap','crew','total_games','total_victories']
    for label in labels:
        if label.startswith("total"):
            other_scores[label] = sum([ prof['otherscores'][label] for prof in profs])
        else:
            other_scores[label] = {
                    'best': 0,
                    'total': 0
                }
            merged_label = other_scores[label]

            for prof in profs:
                profLabel = prof['otherscores'][label]
                merged_label['best'] = max(profLabel['best'], merged_label['best'])
                merged_label['total'] += profLabel['total']
    return other_scores

def merge_crew(profs):
    """
    Merge the crew infos
    """
    crew_skills = []
    best = {}
    for prof in profs:
        for crew_skill in prof['crew_skills']:
            if crew_skill['skillname'] not in best:
                best[crew_skill['skillname']] = crew_skill
            elif best[crew_skill['skillname']]['score'] < crew_skill['score']:
                best[crew_skill['skillname']] = crew_skill
    for skill_name in ['Repair','Combat Kills','Pilot Evasions', 'Jumps Survived', 'Skill Masteries']:
        crew_skills.append(best[skill_name])

    return crew_skills

