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
CARD_ONE = CARD_API + "{}/"

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


IDOL_COLORS = {
    'ayase eli': '36B3DD',
    'hoshizora rin': 'F1C51F',
    'koizumi hanayo': '54AB48',
    'kousaka honoka': 'E2732D',
    'minami kotori': '8C9395',
    'nishikino maki': 'CC3554',
    'sonoda umi': '1660A5',
    'toujou nozomi': '744791',
    'yazawa nico': 'D54E8D',

    'kunikida hanamaru': 'E6D617',
    'kurosawa dia': 'F23B4C',
    'kurosawa ruby': 'FB75E4',
    'matsuura kanan': '13E8AE',
    'ohara mari': 'AE58EB',
    'sakurauchi riko': 'E9A9E8',
    'takami chika': 'F0A20B',
    'tsushima yoshiko': '898989',
    'watanabe you': '49B9F9',
}
IDOLS = {
    'ayase eli': formatting.hex_color('Ayase Eli', IDOL_COLORS['ayase eli']),
    'hoshizora rin': formatting.hex_color('Hoshizora Rin', IDOL_COLORS['hoshizora rin']),
    'koizumi hanayo': formatting.hex_color('Koizumi Hanayo', IDOL_COLORS['koizumi hanayo']),
    'kousaka honoka': formatting.hex_color('Kousaka Honoka', IDOL_COLORS['kousaka honoka']),
    'minami kotori': formatting.hex_color('Minami Kotori', IDOL_COLORS['minami kotori']),
    'nishikino maki': formatting.hex_color('Nishikino Maki', IDOL_COLORS['nishikino maki']),
    'sonoda umi': formatting.hex_color('Sonoda Umi', IDOL_COLORS['sonoda umi']),
    'toujou nozomi': formatting.hex_color('Toujou Nozomi', IDOL_COLORS['toujou nozomi']),
    'yazawa nico': formatting.hex_color('Yazawa Nico', IDOL_COLORS['yazawa nico']),

    'kunikida hanamaru': formatting.hex_color('Kunikida Hanamaru', IDOL_COLORS['kunikida hanamaru']),
    'kurosawa dia': formatting.hex_color('Kurosawa Dia', IDOL_COLORS['kurosawa dia']),
    'kurosawa ruby': formatting.hex_color('Kurosawa Ruby', IDOL_COLORS['kurosawa ruby']),
    'matsuura kanan': formatting.hex_color('Matsuura Kanan', IDOL_COLORS['matsuura kanan']),
    'ohara mari': formatting.hex_color('Ohara Mari', IDOL_COLORS['ohara mari']),
    'sakurauchi riko': formatting.hex_color('Sakurauchi Riko', IDOL_COLORS['sakurauchi riko']),
    'takami chika': formatting.hex_color('Takami Chika', IDOL_COLORS['takami chika']),
    'tsushima yoshiko': formatting.hex_color(
        'Tsushima {} Yohane'.format(formatting.strikethrough('Yoshiko')),
        IDOL_COLORS['ayase eli']
    ),
    'watanabe you': formatting.hex_color('Watanabe You', IDOL_COLORS['watanabe you']),
}


# Some of these are just for convenience, like preventing "umi" from pulling up
# a card of "koizUMI hanayo" instead of "sonoda UMI", or handling alternate
# name spellings (e.g. Eli/Eri).
# Others are official nicknames the characters use for each other in-universe.
IDOL_NICKNAMES = {
    'elicchi': 'ayase eli',
    'eri': 'ayase eli',
    'ericchi': 'ayase eli',
    'kayo-chin': 'koizumi hanayo',
    'kayochin': 'koizumi hanayo',
    'niko': 'yazawa nico',
    'pana': 'koizumi hanayo',
    'umi': 'sonoda umi',

    'riri': 'sakurauchi riko',
    'yohane': 'tsushima yoshiko',
}


RARITIES = {
    'n': 'N',
    'r': 'R',
    'sr': 'SR',
    'ssr': 'SSR',
    'ur': 'UR',
}


# Make SURE to use a lowercase Greek mu (μ) if tweaking anything unit-related!
# Typing <Compose>+mu on Linux yields a micro sign, which is a DIFFERENT code
# point, and μ ≠ µ (confusingly, since in many fonts they look identical).
UNIT_COLORS = {
    'μ\'s': 'E61788',
    'bibi': 'FBDD01',
    'lily white': 'EEFFDD',
    'printemps': 'FABBDD',

    'aqours': '39A0E8',
    'azalea': 'F54DCD',
    'cyaron!': 'F8B646',
    'guilty kiss': 'C398FF',
}
UNITS = {
    'μ\'s': formatting.hex_color('μ\'s', UNIT_COLORS['μ\'s']),
    'bibi': formatting.hex_color('BiBi', UNIT_COLORS['bibi']),
    'lily white': formatting.hex_color('Lily White', UNIT_COLORS['lily white']),
    'printemps': formatting.hex_color('Printemps', UNIT_COLORS['printemps']),

    'aqours': formatting.hex_color('Aqours', UNIT_COLORS['aqours']),
    'azalea': formatting.hex_color('Azalea', UNIT_COLORS['azalea']),
    'cyaron!': formatting.hex_color('CYaRon!', UNIT_COLORS['cyaron!']),
    'guilty kiss': formatting.hex_color('Guilty Kiss', UNIT_COLORS['guilty kiss']),
}


YEARS = {
    'first': "1st",
    'second': "2nd",
    'third': "3rd",
}


class APIError(Exception):
    pass


class InvalidQueryError(Exception):
    pass


def _api_request(url, params={}):
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


def format_idol(idol):
    """Get formatted (colored, etc.) idol name string for output."""
    _idol = idol
    idol = idol.lower()
    if idol not in IDOLS:
        for key in IDOLS.keys():
            if key.startswith(idol) or key.endswith(idol):
                idol = key
                break

    try:
        return IDOLS[idol]
    except KeyError:
        # Not one of the main girls; no color for her
        return _idol


def format_unit(unit):
    """Get formatted (colored, etc.) unit name string for output."""
    if not unit:
        # N cards, EXP/skill teachers, etc. don't have a unit name
        return None

    _unit = unit
    unit = unit.lower()
    if unit not in UNITS:
        for key in UNITS.keys():
            if key.startswith(unit):
                unit = key
                break

    try:
        return UNITS[unit]
    except KeyError:
        # Just give back the input unformatted if it's really, truly unknown
        return _unit


def format_year(year):
    """Get formatted school year string for output."""
    try:
        year = year.lower()
    except AttributeError:
        # Teacher cards and other specials don't have a year
        return None

    return YEARS[year]


def parse_query(query):
    """Parse plain-text query into a tuple of search parameters.

    :param str query: Search query, in plain text, maybe containing keywords
    :return: (text, attribute, rarity, want_promo, want_event)
    :rtype: tuple
    """
    # Split query into words, discarding empty words
    # (e.g. from double-spaces in the query)
    words = filter(None, query.split(' '))
    # Initialize state tracking
    text = []
    rarities = []
    attribute = want_promo = want_event = None

    for word in words:
        _word = word.lower()
        if _word in ATTRIBUTES.keys():
            if attribute:
                # Can't search for multiple attributes (they're mutually exclusive)
                raise InvalidQueryError("You cannot search for multiple attributes.")
            attribute = _word.title()
            continue
        if _word in RARITIES.keys():
            rarities.append(_word.upper())
            continue
        if _word == 'promo':
            want_promo = True
            continue
        if _word == 'non-promo' or _word == '!promo':
            want_promo = False
            continue
        if _word == 'event':
            want_event = True
            continue
        if _word == 'non-event' or _word == '!event':
            want_event = False
            continue
        if _word in IDOL_NICKNAMES.keys():
            text.append(IDOL_NICKNAMES[_word])
            continue
        # Getting here means it's Just Another Keyword
        text.append(word)

    return ' '.join(text), attribute, ','.join(rarities), want_promo, want_event


@module.commands('sifcard')
@module.example('.sifcard')
@module.example('.sifcard jp')
@module.example('.sifcard 123')
@module.example('.sifcard birthday maki ur')
def sif_card(bot, trigger):
    """Fetch LLSIF EN/WW card information.

    Search by card number/ID, or by keywords.

    Special keywords: attribute (Smile/Pure/Cool/All), rarity (N/R/SR/SSR/UR), event/non-event, promo/non-promo
    """
    arg = trigger.group(2)
    params = {}
    url = CARD_API
    if arg is None or arg.lower() in ['en', 'ww']:
        params = LATEST_CARD_PARAMS
        prefix = "Latest SIF EN/WW card: "
    elif arg.lower() == 'jp':
        params = LATEST_CARD_PARAMS.copy()
        del params['japan_only']
        prefix = "Latest SIF JP card: "
    else:
        prefix = ""
        if re.search(r'[^\d]', arg):
            # non-digits in query means run a keyword search
            params = COMMON_SEARCH_PARAMS.copy()
            try:
                text, attribute, rarities, promo, event = parse_query(arg)
            except InvalidQueryError as err:
                return bot.reply("You have an error in your query: {}".format(err))
            params.update({
                'search': text,
                'attribute': attribute,
                'rarity': rarities,
                'is_promo': promo,
                'is_event': event,
            })
        else:
            # query of only digits means run an ID number lookup
            url = CARD_ONE.format(arg)

    try:
        data = _api_request(url, params)
    except APIError as err:
        bot.say("Sorry, something went wrong with the card API.")
        LOGGER.exception("LLSIF API error!")
        return

    if 'results' in data:
        try:
            card = data['results'][0]
        except IndexError:
            bot.reply("No card found!")
            return
    else:
        # I'm sure this will bite me someday, but IDGAF
        card = data

    card_id = card['id']
    character = format_idol(card['idol']['name'])
    attribute = format_attribute(card['attribute'])
    rarity = card['rarity']
    if card['is_promo']:
        rarity = "Promo " + rarity
    if card['is_special']:
        rarity = "Special " + rarity
    released = card['release_date']
    link = card['website_url'].replace('http:', 'https:', 1)

    idol = card['idol']
    try:
        types = ', '.join(filter(None, [
            format_unit(idol['main_unit']),
            format_year(idol['year']),
            format_unit(idol['sub_unit']),
        ]))
    except KeyError:
        types = None

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

    card_extras = ' | '.join(filter(None, [
        types or '',
        '{} set'.format(collection) if collection else '',
    ]))
    if card_extras:
        card_extras = ' | {}'.format(card_extras)

    bot.say("{}[#{}] {} | {} | {}{} | Released: {} | {}".format(
        prefix,
        card_id,
        character,
        attribute,
        rarity,
        card_extras,
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

    title = formatting.hex_color(song['name'], ATTRIBUTE_COLORS[song['attribute'].lower()])
    romaji_title = song['romaji_name']
    english_title = song['translated_name']
    main_unit = format_unit(song['main_unit'])
    attribute = format_attribute(song['attribute'])
    rotation = song['daily_rotation'] or 'A'  # API gives null if not B-sides, for some reason
    duration = song['time']
    duration = "{}:{:0>2}".format(duration // 60, duration % 60)

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
            ' ({})'.format(formatting.italic(romaji_title)) if romaji_title else '',
            duration,
            attribute,
            main_unit,
            'Hits' if rotation == 'A' else 'B-sides',
            ' | '.join(difficulties),
        )
    )
