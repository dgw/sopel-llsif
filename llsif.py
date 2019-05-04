# coding=utf-8
"""
llsif.py - Sopel Love Live! School Idol Festival module
Copyright 2019 dgw
Licensed under the Eiffel Forum License 2

https://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division

import requests

from sopel import module


API_BASE = 'https://schoolido.lu/api/'
CARD_API = API_BASE + 'cards/'

LATEST_CARD_PARAMS = {
    'ordering': '-id',
    'page_size': 1,
    'japan_only': False,
}


@module.commands('sifcard')
@module.example('.sifcard')
def sif_card(bot, trigger):
    """Fetch the latest card added to SIF (worldwide)."""
    try:
        r = requests.get(url=CARD_API, params=LATEST_CARD_PARAMS,
                         timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        bot.say("Connection timed out.")
        return
    except requests.exceptions.ConnectionError:
        bot.say("Couldn't connect to server.")
        return
    except requests.exceptions.ReadTimeout:
        bot.say("Server took too long to send data.")
        return
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        bot.say("HTTP error: " + e.message)
        return
    try:
        data = r.json()
    except ValueError:
        bot.say("Couldn't decode API response: " + r.content)
        return

    card = data['results'][0]

    card_id = card['id']
    character = card['idol']['name']
    attribute = card['attribute']
    rarity = card['rarity']
    released = card['release_date']
    link = card['website_url'].replace('http:', 'https:', 1)

    bot.say("Latest SIF WW card: {} {} {} (#{}), released {} — {}"
            .format(character, attribute, rarity, card_id, released, link))