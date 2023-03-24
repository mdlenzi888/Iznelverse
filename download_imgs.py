from character_list import characters
import requests
from urllib.request import urlopen
import json
import os

data = {
    'grant_type': 'client_credentials'
}

client_id = os.getenv('wow-client-id')
client_secret = os.getenv('wow-client-secret')
access_token = requests.post('https://us.battle.net/oauth/token',
                             data=data,
                             auth=(f'{client_id}', f'{client_secret}')
                             ).json()['access_token']

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


def download_spec_img():
    response_all_specs = urlopen(f'https://us.api.blizzard.com/data/wow/playable-specialization/index?namespace=static-us&locale=en_US&access_token={access_token}')
    json_all_specs = json.loads(response_all_specs.read())

    for spec in json_all_specs['character_specializations']:
        spec_id = spec['id']
        response_spec_img = urlopen(f'https://us.api.blizzard.com/data/wow/media/playable-specialization/{spec_id}?namespace=static-us&locale=en_US&access_token={access_token}')
        json_spec_img = json.loads(response_spec_img.read())

        img_url = json_spec_img['assets'][0]['value']
        img_data = requests.get(img_url).content

        with open(f'static/images/specs/spec-img-{spec_id}.jpg', 'wb') as handler:
            handler.write(img_data)


def download_character_img():
    for key in characters:
        response_char_img = urlopen(f"https://us.api.blizzard.com/profile/wow/character/{characters[key][0]}/{key}/character-media?namespace=profile-us&locale=en_US&access_token={access_token}")
        json_response_char_img = json.loads(response_char_img.read())

        img_url = json_response_char_img['assets'][0]['value']
        img_data = requests.get(img_url).content

        with open(f'static/images/characters/{key}-head.jpg', 'wb') as handler:
            handler.write(img_data)

        img_url = json_response_char_img['assets'][2]['value']
        img_data = requests.get(img_url).content

        with open(f'static/images/characters/{key}-body.jpg', 'wb') as handler:
            handler.write(img_data)


def download_pvp_rating_img():
    response_pvp_tiers = urlopen(
        f'https://us.api.blizzard.com/data/wow/pvp-tier/index?namespace=static-us&locale=en_US&access_token={access_token}')
    json_pvp_tiers = json.loads(response_pvp_tiers.read())

    for spec in json_pvp_tiers['tiers']:
        response_pvp_rating_img = urlopen(f"https://us.api.blizzard.com/data/wow/media/pvp-tier/{spec['id']}?namespace=static-us&locale=en_US&access_token={access_token}")
        json_pvp_rating_img = json.loads(response_pvp_rating_img.read())

        img_url = json_pvp_rating_img['assets'][0]['value']
        img_data = requests.get(img_url).content

        with open(f'static/images/pvp-tiers/tier-{spec["id"]}.jpg', 'wb') as handler:
            handler.write(img_data)


def download_instance_img():
    for dungeon_name, dungeon_id, instance_id in CURRENT_MYTHIC_DUNGEONS:
        response_instance_img = urlopen(f"https://us.api.blizzard.com/data/wow/media/journal-instance/{instance_id}?namespace=static-us&locale=en_US&access_token={access_token}")
        json_instance_img = json.loads(response_instance_img.read())

        img_url = json_instance_img['assets'][0]['value']
        img_data = requests.get(img_url).content
        with open(f'static/images/instances/instance-{instance_id}.jpg', 'wb') as handler:
            handler.write(img_data)

    raid_id = CURRENT_RAID[1]
    response_instance_img = urlopen(f"https://us.api.blizzard.com/data/wow/media/journal-instance/{raid_id}?namespace=static-us&locale=en_US&access_token={access_token}")
    json_instance_img = json.loads(response_instance_img.read())

    img_url = json_instance_img['assets'][0]['value']
    img_data = requests.get(img_url).content
    with open(f'static/images/instances/instance-{raid_id}.jpg', 'wb') as handler:
        handler.write(img_data)


def download_all():
    # download_spec_img()
    download_character_img()
    # download_pvp_rating_img()
    # download_instance_img()


download_all()
