# coding=utf-8
"""
llsif.py - Sopel Love Live! School Idol Festival module
Copyright 2019 dgw
Licensed under the Eiffel Forum License 2

https://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division

import re

import requests

from sopel.logger import get_logger
from sopel import formatting, module


API_BASE = 'https://schoolido.lu/api/'
CARD_API = API_BASE + 'cards/'
SONG_API = API_BASE + 'songs/'

LATEST_CARD_PARAMS = {
    'ordering': '-id',
    'page_size': 1,
    'japan_only': False,
}

COMMON_SEARCH_PARAMS = {
    'page_size': 1,
}


LOGGER = get_logger(__name__)


ATTRIBUTE_COLORS = {
    'smile': 'F16DB8',
    'pure': '11BD11',
    'cool': '41A2F5',
    'all': 'C956FC',
}
ATTRIBUTES = {
    'smile': formatting.hex_color('Smile', ATTRIBUTE_COLORS['smile']),
    'pure': formatting.hex_color('Pure', ATTRIBUTE_COLORS['pure']),
    'cool': formatting.hex_color('Cool', ATTRIBUTE_COLORS['cool']),
    'all': formatting.hex_color('Universal', ATTRIBUTE_COLORS['all'])
}


class APIError(Exception):
    pass


def _api_request(url, params):
    try:
        r = requests.get(url=url, params=params,
                         timeout=(10.0, 4.0))
    except requests.exceptions.ConnectTimeout:
        raise APIError("Connection timed out.")
    except requests.exceptions.ConnectionError:
        raise APIError("Couldn't connect to server.")
    except requests.exceptions.ReadTimeout:
        raise APIError("Server took too long to send data.")
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise APIError("HTTP error: " + e.message)
    try:
        data = r.json()
    except ValueError:
        raise APIError("Couldn't decode API response: " + r.content)

    return data


def format_attribute(attribute):
    """Get formatted (colored, etc.) attribute string for output."""
    attribute = attribute.lower()
    if attribute not in ATTRIBUTES:
        for key in ATTRIBUTES.keys():
            if key.startswith(attribute):
                attribute = key
                break

    return ATTRIBUTES[attribute]


@module.commands('sifcard')
@module.example('.sifcard')
@module.example('.sifcard jp')
@module.example('.sifcard birthday maki')
@module.example('.sifcard 123')
def sif_card(bot, trigger):
    """Fetch LLSIF EN/WW card information."""
    arg = trigger.group(2)
    if arg is None or arg.lower() in ['en', 'ww']:
        params = LATEST_CARD_PARAMS
        prefix = "Latest SIF EN/WW card: "
    elif arg.lower() == 'jp':
        params = LATEST_CARD_PARAMS.copy()
        del params['japan_only']
        prefix = "Latest SIF JP card: "
    else:
        params = COMMON_SEARCH_PARAMS.copy()
        prefix = ""
        if re.search(r'[^\d]', arg):
            # non-digits in query means run a keyword search
            params.update({'search': arg})
        else:
            # query of only digits means run an ID number lookup
            params.update({'ids': arg})

    try:
        data = _api_request(CARD_API, params)
    except APIError as err:
        bot.say("Sorry, something went wrong with the card API.")
        LOGGER.exception("LLSIF API error!")
        return

    try:
        card = data['results'][0]
    except IndexError:
        bot.reply("No card found!")
        return

    card_id = card['id']
    character = card['idol']['name']
    attribute = format_attribute(card['attribute'])
    rarity = card['rarity']
    released = card['release_date']
    link = card['website_url'].replace('http:', 'https:', 1)

    collection = card.get('translated_collection', '')
    if not collection:
        # No localized name; use Japanese
        collection = card.get('japanese_collection', '')
        if not collection:
            # No Japanese name either?! Give up, then.
            pass
        else:
            # Quote name in Japanese style
            collection = "「{}」".format(collection)
    else:
        # Quote name in English style
        collection = '"{}"'.format(collection)

    bot.say("{}{} {} {} (#{}{}), released {} — {}".format(
        prefix,
        character,
        attribute,
        rarity,
        card_id,
        ', {} set'.format(collection) if collection else '',
        released,
        link,
    ))


@module.commands('sifsong')
@module.example('.sifsong snow halation')
def sif_song(bot, trigger):
    """Look up LLSIF live show information."""
    params = COMMON_SEARCH_PARAMS.copy()
    if not trigger.group(2):
        params.update({'ordering': 'random'})
    else:
        params.update({'search': trigger.group(2)})

    try:
        data = _api_request(SONG_API, params)
    except APIError:
        bot.say("Sorry, something went wrong with the song API.")
        LOGGER.exception("LLSIF API error!")
        return

    try:
        song = data['results'][0]
    except IndexError:
        bot.reply("No song found!")
        return

    title = song['name']
    romaji_title = song['romaji_name']
    english_title = song['translated_name']
    main_unit = song['main_unit']
    attribute = format_attribute(song['attribute'])
    rotation = song['daily_rotation'] or 'A'  # API gives null if not B-sides, for some reason
    duration = song['time']
    duration = "{}:{:0>2}".format(duration // 60, duration % 60)

    title_extras = ''
    if romaji_title or english_title:
        title_extras = ' ({})'.format(', '.join(filter(None, [
            formatting.italic(romaji_title) if romaji_title else '',
            '"{}"'.format(english_title) if english_title else '',
        ])))

    difficulties = []
    for level in ['easy', 'normal', 'hard', 'expert', 'master']:
        key_notes = level + '_notes'
        key_stars = level + '_difficulty'
        # skip difficulty level if it has null for either value
        if song[key_notes] and song[key_stars]:
            difficulties.append(
                '{}: {}🟊, {} notes'.format(
                    level.title(),
                    song[key_stars],
                    song[key_notes],
                )
            )

    bot.say("{}{} [{}] | {}, in {} {} — {}"
        .format(
            title,
            title_extras,
            duration,
            attribute,
            main_unit,
            'Hits' if rotation == 'A' else 'B-sides',
            ' | '.join(difficulties),
        )
    )
