import urllib.error
import os
from character_list import characters
import requests
from urllib.request import urlopen
import json

data = {
    'grant_type': 'client_credentials'
}

client_id = os.environ.get("WOW_ID")
client_secret = os.environ.get("WOW_SECRET")
token_request = requests.post('https://us.battle.net/oauth/token',
                              data=data,
                              auth=(f'{client_id}', f'{client_secret}')
                              )
access_token = token_request.json()['access_token']

CURRENT_PVP_SEASON = 34
CURRENT_MYTHIC_SEASON = 9
CURRENT_MYTHIC_DUNGEONS = [('Temple of the Jade Serpent', 2, 313),
                           ('Shadowmoon Burial Grounds', 165, 537),
                           ('Halls of Valor', 200, 721),
                           ('Court of Stars', 210, 800),
                           ('Ruby Life Pools', 399, 1202),
                           ('The Nokhud Offensive', 400, 1198),
                           ("The Azure Vault", 401, 1203),
                           ("Algeth'ar Academy", 402, 1201)]
# (name, dungeon id, instance id)
CURRENT_RAID = ('Vault of the Incarnates', 1200)
RAID_DIFFICULTIES = ['Raid Finder', 'Normal', 'Heroic', 'Mythic']


class Character:
    def __init__(self, char):
        self.name = char
        self.realm = characters[char][0]
        self.faction = ""
        self.race = ""
        self.char_class = ""
        self.spec = ""
        self.spec_id = ""
        self.guild = ""
        self.lvl = 0
        self.ilvl = 0
        # self.cov = ""
        self.talents = {
            'pve': [],
            'pvp': []
        }  # {'pve': [{'id': '23146', 'name': 'Feral Frenzy'}, etc.], 'pvp': etc.}
        self.gear = []  # [{'id': 186796, 'name': 'Cosmic Gladiator's Silk Hood', 'quality': 'epic'}, etc.]
        self.pvp_ratings = []  # ['bracket': '2v2','rating': 1650, 'tier': challenger II}, etc.]
        self.dungeons = CURRENT_MYTHIC_DUNGEONS
        self.mythic_plus = {
            'score': 0,
            'color': 'grey',
            'instances': {}
        }  # {'score': 1850, 'quality': {}, 'instances': [{'name': 'Mists', 'highest_lvl': 14, 'score': 243, 'quality': red}, etc.]}
        for dung in CURRENT_MYTHIC_DUNGEONS:
            self.mythic_plus['instances'][dung[0]] = {
                'id': dung[2],
                'highest_lvl': '-',
                'score': '-',
                'quality': 'grey'
            }
        self.char_id = characters[char][1]
        self.raid_logs = {
            'name': '',
            'id': 0,
            'progress': {
                'difficulty': 'normal',
                'count': '9/11'
            },
            'bosses': []
        }  # {'name': 'Seplechur of The First Ones', 'id': 1195, 'progress': {'difficulty': 'normal', 'count': '9/11'}, 'bosses': [{'name': Vigilante Guardians, 'parse': 45}, etc.]}

        self.get_char_info()
        self.get_talents()
        self.get_gear()
        self.get_pvp_ratings()
        self.get_mythic_plus()
        self.get_raid_logs()

    def get_char_info(self):
        try:
            response_char_info = urlopen(
                f"https://us.api.blizzard.com/profile/wow/character/{self.realm}/{self.name}?namespace=profile-us&locale=en_US&access_token={access_token}")
            json_char_info = json.loads(response_char_info.read())

            self.faction = json_char_info['faction']['name']
            self.race = json_char_info['race']['name']
            self.char_class = json_char_info['character_class']['name']
            self.spec = json_char_info['active_spec']['name']
            self.spec_id = json_char_info['active_spec']['id']
            try:
                self.guild = json_char_info['guild']['name']
            except KeyError:
                pass
            self.lvl = json_char_info['level']
            self.ilvl = json_char_info['equipped_item_level']
            # self.cov = json_char_info['covenant_progress']['chosen_covenant']['name']

            print("Got Char Info")
        except urllib.error.URLError:
            self.get_char_info()

    def get_talents(self):
        try:
            response_talents = urlopen(
                f"https://us.api.blizzard.com/profile/wow/character/{self.realm}/{self.name}/specializations?namespace=profile-us&locale=en_US&access_token={access_token}")
            json_response_talents = json.loads(response_talents.read())
            for spec in json_response_talents['specializations']:
                if self.spec == spec['specialization']['name']:
                    for talent in spec['loadouts'][0]['selected_spec_talents']:
                        self.talents['pve'].append(
                            {'id': talent['tooltip']['spell_tooltip']['spell']['id'],
                             'name': talent['tooltip']['spell_tooltip']['spell']['name']}
                        )
                    for talent in spec['pvp_talent_slots']:
                        self.talents['pvp'].append(
                            {'id': talent['selected']['spell_tooltip']['spell']['id'],
                             'name': talent['selected']['spell_tooltip']['spell']['name']}
                        )
            print("Got Talents")
        except urllib.error.URLError:
            self.get_talents()

    def get_gear(self):
        try:
            response_gear = urlopen(
                f"https://us.api.blizzard.com/profile/wow/character/{self.realm}/{self.name}/equipment?namespace=profile-us&locale=en_US&access_token={access_token}")
            json_response_gear = json.loads(response_gear.read())
            for item in json_response_gear['equipped_items']:
                self.gear.append({
                    'id': item['item']['id'],
                    'name': item['name'],
                    'ilvl': item['level']['value'],
                    'quality': item['quality']['name'].lower(),
                })
            print("Got Gear")
        except urllib.error.URLError:
            self.get_gear()

    def get_pvp_ratings(self):
        brackets = {
            'Solo': f'shuffle-{self.char_class.lower()}-{self.spec.lower()}',
            '2v2': '2v2',
            '3v3': '3v3',
            'rBG': 'rbg'
            }
        for title, code in brackets.items():
            try:
                response_pvp_ratings = urlopen(
                    f"https://us.api.blizzard.com/profile/wow/character/{self.realm}/{self.name}/pvp-bracket/{code}?namespace=profile-us&locale=en_US&access_token={access_token}")
                json_pvp_ratings = json.loads(response_pvp_ratings.read())

                if json_pvp_ratings['season']['id'] == CURRENT_PVP_SEASON:
                    self.pvp_ratings.append({
                        'bracket': title,
                        'rating': json_pvp_ratings['rating'],
                        'tier': json_pvp_ratings['tier']['id']
                    })
                else:
                    self.pvp_ratings.append({
                        'bracket': title,
                        'rating': 0,
                        'tier': 1
                    })
            except urllib.error.URLError:
                self.pvp_ratings.append({
                    'bracket': title,
                    'rating': 0,
                    'tier': 1
                })
        print("Got PVP Ratings")

    def get_mythic_plus(self):
        try:
            response_mythic_plus = urlopen(
                f"https://us.api.blizzard.com/profile/wow/character/{self.realm}/{self.name}/mythic-keystone-profile/season/{CURRENT_MYTHIC_SEASON}?namespace=profile-us&locale=en_US&access_token={access_token}")
            json_mythic_plus = json.loads(response_mythic_plus.read())
            print(json_mythic_plus)

            self.mythic_plus['score'] = round(json_mythic_plus['mythic_rating']['rating'])
            if self.mythic_plus['score'] >= 2400:
                quality = 'legendary'
            elif self.mythic_plus['score'] >= 1600:
                quality = 'epic'
            elif self.mythic_plus['score'] >= 960:
                quality = 'rare'
            elif self.mythic_plus['score'] >= 480:
                quality = 'uncommon'
            else:
                quality = 'grey'
            self.mythic_plus['quality'] = quality

            for dungeon in json_mythic_plus['best_runs']:
                if round(dungeon['map_rating']['rating']) >= 220:
                    quality = 'legendary'
                elif round(dungeon['map_rating']['rating']) >= 200:
                    quality = 'epic'
                elif round(dungeon['map_rating']['rating']) >= 180:
                    quality = 'rare'
                elif round(dungeon['map_rating']['rating']) >= 130:
                    quality = 'uncommon'
                else:
                    quality = 'grey'

                if dungeon['dungeon']['name'] in self.mythic_plus['instances']:
                    self.mythic_plus['instances'][dungeon['dungeon']['name']]['highest_lvl'] = dungeon['keystone_level']
                    self.mythic_plus['instances'][dungeon['dungeon']['name']]['score'] = round(
                        dungeon['map_rating']['rating'])
                    self.mythic_plus['instances'][dungeon['dungeon']['name']]['quality'] = quality
            print("Got Mythic Ratings")
        except (urllib.error.HTTPError, urllib.error.URLError):
            pass

    def get_raid_logs(self):
        try:
            logs_id = os.environ.get("LOGS_ID")
            logs_secret = os.environ.get("LOGS_SECRET")
            logs_data = {
                'grant_type': 'client_credentials'
            }
            path = "https://www.warcraftlogs.com/oauth/token"
            logs_token = requests.post(path,
                                       data=logs_data,
                                       auth=(f'{logs_id}', f'{logs_secret}')
                                       ).json()['access_token']
            my_data = """query {
                characterData{
                    character(id: """ + self.char_id + """) {
                        classID
                        name
                        level
                        zoneRankings
                        gameData
                    }
                }
            }"""
            header = {
                'Authorization': f'Bearer {logs_token}'
            }
            response_raid_logs = requests.get('https://www.warcraftlogs.com/api/v2/client', headers=header,
                                              json={'query': my_data})
            json_raid_logs = response_raid_logs.json()
            print(json_raid_logs)

            raid = json_raid_logs['data']['characterData']['character']['zoneRankings']

            self.raid_logs['name'] = CURRENT_RAID[0]
            self.raid_logs['id'] = CURRENT_RAID[1]
            self.raid_logs['progress']['difficulty'] = RAID_DIFFICULTIES[raid['difficulty'] - 1]

            completed_count = 0
            for boss in json_raid_logs['data']['characterData']['character']['zoneRankings']['rankings']:
                if boss['rankPercent'] is None:
                    self.raid_logs['bosses'].append({
                        'name': boss['encounter']['name'],
                        'id': boss['encounter']['id'],
                        'parse': '-',
                        'quality': 'grey'
                    })
                else:
                    completed_count += 1
                    parse = round(boss['rankPercent'])
                    if parse >= 100:
                        quality = 'gold'
                    elif parse >= 95:
                        quality = 'ascended'
                    elif parse >= 80:
                        quality = 'epic'
                    elif parse >= 50:
                        quality = 'rare'
                    elif parse >= 25:
                        quality = 'uncommon'
                    else:
                        quality = 'grey'
                    self.raid_logs['bosses'].append({
                        'name': boss['encounter']['name'],
                        'id': boss['encounter']['id'],
                        'parse': parse,
                        'quality': quality
                    })
            total_count = len(self.raid_logs['bosses'])
            self.raid_logs['progress'][
                'count'] = f"{completed_count}/{total_count}"

            print("Got Raid Logs")
        except urllib.error.URLError:
            self.get_raid_logs()
