"""Spelling category - Detects common misspellings."""
from typing import List, Tuple
from .base_category import BaseCategory

class SpellingCategory(BaseCategory):
    def get_category_name(self) -> str:
        return 'spelling'
    
    def get_display_name(self) -> str:
        return 'Spelling'
    
    def get_patterns(self) -> List[Tuple]:
        return []
    
    def get_dictionary(self) -> dict:
        return {
            'accomodate': 'accommodate',
            'acheive': 'achieve',
            'alot': 'a lot',
            'alright': 'all right',
            'arguement': 'argument',
            'basicly': 'basically',
            'begining': 'beginning',
            'beleive': 'believe',
            'calender': 'calendar',
            'catagory': 'category',
            'cemetary': 'cemetery',
            'changable': 'changeable',
            'collegue': 'colleague',
            'comming': 'coming',
            'commitee': 'committee',
            'completly': 'completely',
            'concious': 'conscious',
            'definately': 'definitely',
            'desparate': 'desperate',
            'diffrent': 'different',
            'dissapoint': 'disappoint',
            'embarass': 'embarrass',
            'enviroment': 'environment',
            'existance': 'existence',
            'experiance': 'experience',
            'explaination': 'explanation',
            'familar': 'familiar',
            'february': 'February',
            'finaly': 'finally',
            'fourty': 'forty',
            'freind': 'friend',
            'goverment': 'government',
            'grammer': 'grammar',
            'gratefull': 'grateful',
            'greatful': 'grateful',
            'happend': 'happened',
            'harrassment': 'harassment',
            'hieght': 'height',
            'humerous': 'humorous',
            'ignorence': 'ignorance',
            'immediatly': 'immediately',
            'independant': 'independent',
            'indispensable': 'indispensable',
            'jewelery': 'jewelry',
            'judgement': 'judgment',
            'knowlege': 'knowledge',
            'liason': 'liaison',
            'libary': 'library',
            'maintainance': 'maintenance',
            'maneuver': 'maneuver',
            'millenium': 'millennium',
            'mischevious': 'mischievous',
            'misspell': 'misspell',
            'necessery': 'necessary',
            'neccessary': 'necessary',
            'noticable': 'noticeable',
            'occured': 'occurred',
            'occurence': 'occurrence',
            'occassion': 'occasion',
            'personnell': 'personnel',
            'posession': 'possession',
            'prefered': 'preferred',
            'priviledge': 'privilege',
            'probaly': 'probably',
            'recieve': 'receive',
            'recomend': 'recommend',
            'refered': 'referred',
            'relevent': 'relevant',
            'religous': 'religious',
            'remeber': 'remember',
            'repitition': 'repetition',
            'sence': 'sense',
            'seperate': 'separate',
            'succesful': 'successful',
            'supercede': 'supersede',
            'suprise': 'surprise',
            'temperture': 'temperature',
            'tommorrow': 'tomorrow',
            'truely': 'truly',
            'unfortunatly': 'unfortunately',
            'untill': 'until',
            'useable': 'usable',
            'vaccuum': 'vacuum',
            'wierd': 'weird',
            'whereever': 'wherever',
        }
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        return 0.95

