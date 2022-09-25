# coding=utf-8
"""
llsif.py - Sopel Love Live! School Idol Festival plugin
Copyright 2019-2022 dgw, technobabbl.es
Licensed under the Eiffel Forum License 2

https://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division

import datetime
import random
import re

import requests
from scheduler import Scheduler
import scheduler.trigger as schedule_trigger

from sopel.config import types
from sopel.logger import get_logger
from sopel import formatting, module


def _send_rc_5x(bot):
    channels = bot.config.llsif.rc_5x_channels or bot.channels.keys()

    for channel in channels:
        bot.say("[LLSIF] Rhythmic Carnival 5x EXP hour has started!", channel)


UTC = datetime.timezone.utc

RC_5X_TIMES = [
    datetime.time(hour=3, tzinfo=UTC),
    datetime.time(hour=8, tzinfo=UTC),
    datetime.time(hour=12, tzinfo=UTC),
]


class LLSIFSection(types.StaticSection):
    rc_5x_notify = types.BooleanAttribute('rc_5x_notify', default=False)
    rc_5x_channels = types.ListAttribute('rc_5x_channels')


def setup(bot):
    bot.config.define_section('llsif', LLSIFSection)

    if not bot.config.llsif.rc_5x_notify:
        return

    schedule = Scheduler(tzinfo=UTC)

    scheduled_jobs = [
        schedule_trigger.Saturday(t) for t in RC_5X_TIMES
    ]
    scheduled_jobs += [
        schedule_trigger.Sunday(t) for t in RC_5X_TIMES
    ]

    schedule.weekly(scheduled_jobs, _send_rc_5x, args=(bot,))

    bot.memory['llsif_scheduler'] = schedule


def shutdown(bot):
    try:
        bot.memory['llsif_scheduler'].delete_jobs()
        del bot.memory['llsif_scheduler']
    except KeyError:
        pass


@module.interval(30)
def scheduler_run(bot):
    if 'llsif_scheduler' not in bot.memory:
        return

    bot.memory['llsif_scheduler'].exec_jobs()


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

    'kira tsubasa': 'C5A06B',
    'toudou erena': '8F44A6',
    # probably fine to have 'yuuki' as an alias for Setsuna
    # A-RISE cards aren't very common
    'yuuki anju': 'DD6722',

    'kunikida hanamaru': 'E6D617',
    'kurosawa dia': 'F23B4C',
    'kurosawa ruby': 'FB75E4',
    'matsuura kanan': '13E8AE',
    'ohara mari': 'AE58EB',
    'sakurauchi riko': 'E9A9E8',
    'takami chika': 'F0A20B',
    'tsushima yoshiko': '898989',
    'watanabe you': '49B9F9',

    'asaka karin': '565EA9',
    'emma verde': '8EC225',
    'konoe kanata': 'B44E8F',
    'miyashita ai': 'F18F3D',
    'nakasu kasumi': 'FFE41C',
    'ousaka shizuku': '73C9F3',
    'mifune shioriko': '39B184',
    'tennoji rina': '9AA3AA',
    'uehara ayumu': 'EE879D',
    'yuki setsuna': 'E94C53',

    'arashi chisato': 'FF6E91',
    'hazuki ren': '0100A0',
    'heanna sumire': '74F467',
    'shibuya kanon': 'FF7F27',
    'tang keke': 'A0FFF9',
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

    'kira tsubasa': formatting.hex_color('Kira Tsubasa', IDOL_COLORS['kira tsubasa']),
    'toudou erena': formatting.hex_color('Toudou Erena', IDOL_COLORS['toudou erena']),
    # probably fine to have 'yuuki' as an alias for Setsuna
    # A-RISE cards aren't very common
    'yuuki anju': formatting.hex_color('Yuuki Anju', IDOL_COLORS['yuuki anju']),

    'kunikida hanamaru': formatting.hex_color('Kunikida Hanamaru', IDOL_COLORS['kunikida hanamaru']),
    'kurosawa dia': formatting.hex_color('Kurosawa Dia', IDOL_COLORS['kurosawa dia']),
    'kurosawa ruby': formatting.hex_color('Kurosawa Ruby', IDOL_COLORS['kurosawa ruby']),
    'matsuura kanan': formatting.hex_color('Matsuura Kanan', IDOL_COLORS['matsuura kanan']),
    'ohara mari': formatting.hex_color('Ohara Mari', IDOL_COLORS['ohara mari']),
    'sakurauchi riko': formatting.hex_color('Sakurauchi Riko', IDOL_COLORS['sakurauchi riko']),
    'takami chika': formatting.hex_color('Takami Chika', IDOL_COLORS['takami chika']),
    'tsushima yoshiko': formatting.hex_color(
        'Tsushima {} Yohane'.format(formatting.strikethrough('Yoshiko')),
        IDOL_COLORS['tsushima yoshiko']
    ),
    'watanabe you': formatting.hex_color('Watanabe You', IDOL_COLORS['watanabe you']),

    'asaka karin': formatting.hex_color('Asaka Karin', IDOL_COLORS['asaka karin']),
    'emma verde': formatting.hex_color('Emma Verde', IDOL_COLORS['emma verde']),
    'konoe kanata': formatting.hex_color('Konoe Kanata', IDOL_COLORS['konoe kanata']),
    'miyashita ai': formatting.hex_color('Miyashita Ai', IDOL_COLORS['miyashita ai']),
    'nakasu kasumi': formatting.hex_color('Nakasu Kasumi', IDOL_COLORS['nakasu kasumi']),
    'ousaka shizuku': formatting.hex_color('Ousaka Shizuku', IDOL_COLORS['ousaka shizuku']),
    'mifune shioriko': formatting.hex_color('Mifune Shioriko', IDOL_COLORS['mifune shioriko']),
    'tennoji rina': formatting.hex_color('Tennoji Rina', IDOL_COLORS['tennoji rina']),
    'uehara ayumu': formatting.hex_color('Uehara Ayumu', IDOL_COLORS['uehara ayumu']),
    'yuki setsuna': formatting.hex_color('Yuki Setsuna', IDOL_COLORS['yuki setsuna']),

    'arashi chisato': formatting.hex_color('Arashi Chisato', IDOL_COLORS['arashi chisato']),
    'hazuki ren': formatting.hex_color('Hazuki Ren', IDOL_COLORS['hazuki ren']),
    'heanna sumire': formatting.hex_color('Heanna Sumire', IDOL_COLORS['heanna sumire']),
    'shibuya kanon': formatting.hex_color('Shibuya Kanon', IDOL_COLORS['shibuya kanon']),
    'tang keke': formatting.hex_color('Tang Keke', IDOL_COLORS['tang keke']),
}


# Some of these are just for convenience, like preventing "umi" from pulling up
# a card of "koizUMI hanayo" instead of "sonoda UMI", or handling alternate
# name spellings (e.g. Eli/Eri).
# Others are official nicknames the characters use for each other in-universe.
# In `parse_card_query()`, hyphens are removed from the input to reduce the amount of
# duplication needed in this dictionary.
IDOL_NICKNAMES = {
    'elicchi': 'ayase eli',
    'eri': 'ayase eli',
    'ericchi': 'ayase eli',
    'kayochin': 'koizumi hanayo',
    'niko': 'yazawa nico',
    'nontan': 'toujou nozomi',
    'pana': 'koizumi hanayo',
    'umi': 'sonoda umi',

    'riri': 'sakurauchi riko',
    'yohane': 'tsushima yoshiko',

    'osaka': 'ousaka shizuku',
    'tennouji': 'tennoji rina',
    'yuuki': 'setsuna yuki',

    'kuku': 'tang keke',
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


class NoResultError(Exception):
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
        if r.status_code == 404:
            # treat 404 as if the server sent an empty result
            return {'results': []}
        # otherwise bubble up the error message
        raise APIError("HTTP error: " + str(e))
    try:
        data = r.json()
    except ValueError:
        raise APIError("Couldn't decode API response: " + r.content)

    return data


def _bond_points(combo):
    """Get bond/kizuna points awarded for a given combo string."""
    under_200 = min(200, combo)
    over_200 = max(0, combo - 200)
    return (
        (combo // 10) +
        (over_200 // 10) +
        (4 * (combo // 50)) -
        (over_200 // 50) +
        (5 * (combo // 100))
    )


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


def parse_card_query(query):
    """Parse plain-text query into a tuple of card search parameters.

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
        # Use lowercase version with hyphens removed for comparisons
        # Hyphen filter helps avoid duplicating too many IDOL_NICKNAMES mappings
        # (The benefit of transforming to lowercase is obvious.)
        _word = word.lower().replace('-', '')
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


def parse_song_query(query):
    """Parse plain-text query into a tuple of song search parameters.

    :param str query: Search query, in plain text, maybe containing keywords
    :return: (text, attribute, is_event)
    :rtype: tuple
    :raise InvalidQueryError: when the query contains conflicting operators
    """
    # Split query into words, discarding empty words
    # (e.g. from double-spaces in the query)
    words = filter(None, query.split(' '))
    # Initialize state tracking
    text = []
    attribute = is_event = None

    for word in words:
        _word = word.lower().replace('-', '')
        if _word in ATTRIBUTES.keys():
            if attribute:
                # Can't search for multiple attributes (they're mutually exclusive)
                raise InvalidQueryError("You cannot search for multiple attributes.")
            attribute = _word.title()
            continue
        if _word == 'event':
            is_event = True
            continue
        if _word == 'non-event' or _word == '!event':
            is_event = False
            continue
        # Getting here means it's Just Another Keyword
        text.append(word)

    return ' '.join(text), attribute, is_event


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
                text, attribute, rarities, promo, event = parse_card_query(arg)
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
    school = card['idol']['school']
    attribute = format_attribute(card['attribute'])
    rarity = card['rarity']
    if card['is_promo']:
        rarity = "Promo " + rarity
    if card['is_special']:
        rarity = "Special " + rarity
    released = card['release_date']
    link = card['website_url'].replace('http:', 'https:', 1)
    # remove stupid trailing directory after card ID
    link = re.sub(r'(.+\/).+', r'\1', link)

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
        school or '',
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


def _get_song(query):
    """Get a song from the API that matches the query.

    :param str query: the user's search query
    :return: the song object
    :rtype: dict
    :raise NoResultError: if the query doesn't match any songs
    :raise APIError: if there is an error accessing the API
    :raise InvalidQueryError: if the query contains conflicting operators
    """
    params = COMMON_SEARCH_PARAMS.copy()
    if query:
        text, attribute, is_event = parse_song_query(query)
        params.update({
            'search': text,
            'attribute': attribute,
            'is_event': is_event,
        })

    if not query or not text:
        params.update({'ordering': 'random'})

    try:
        data = _api_request(SONG_API, params)
    except APIError:
        LOGGER.exception("LLSIF API error!")
        raise

    try:
        song = data['results'][0]
    except IndexError:
        raise NoResultError

    return song


def _get_song_level_info(song):
    info = {}

    for level in ['easy', 'normal', 'hard', 'expert', 'master']:
        key_notes = level + '_notes'
        key_stars = level + '_difficulty'
        # skip difficulty level if it has null for either value
        if song[key_notes] and song[key_stars]:
            info[level] = {
                'stars': song[key_stars],
                'notes': song[key_notes],
            }

    return info


@module.commands('sifsong')
@module.example('.sifsong snow halation')
def sif_song(bot, trigger):
    """Look up LLSIF live show information.

    Special keywords: song attribute (Smile, Pure, Cool), and whether the song
    was an event song (event, !event, or non-event).
    """
    try:
        song = _get_song(trigger.group(2))
    except APIError:
        bot.say("Sorry, something went wrong with the song API.")
        return
    except NoResultError:
        bot.reply("No song found!")
        return
    except InvalidQueryError as err:
        bot.reply("You have an error in your query: {}".format(err))
        return

    title = formatting.hex_color(song['name'], ATTRIBUTE_COLORS[song['attribute'].lower()])
    romaji_title = song['romaji_name']
    english_title = song['translated_name']
    main_unit = format_unit(song['main_unit'])
    attribute = format_attribute(song['attribute'])
    rotation = song['daily_rotation'] or 'A'  # API gives null if not B-sides, for some reason
    duration = song['time']
    if duration is None:
        duration = '?:??'
    else:
        duration = "{}:{:0>2}".format(duration // 60, duration % 60)

    difficulties = [
        '{}: {}🟊, {} notes, {} kizuna'.format(
            level.title(),
            info['stars'],
            info['notes'],
            _bond_points(info['notes']),
        ) for level, info in _get_song_level_info(song).items()
    ]

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
