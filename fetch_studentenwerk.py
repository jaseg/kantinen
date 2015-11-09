#!/usr/bin/env python3

import bs4, requests, argparse
from decimal import Decimal
from datetime import datetime
import os.path


DEFAULT_CATS = {
        'tu': (('special', 'Spezial'), ('food', 'Standard'), ('soups', 'Suppen')),
        'tu_cafe_erp': (('special', 'Spezial'),),
        'tu_cafe_skyline': (('daily_offer',' Tages'),),
        'tu_marchstr': (('special', 'Spezial'), ('daily_offer','Tages'))}
LOC_SHORTNAME_MAP = {
        'skyline': 'tu_cafe_skyline',
        'main': 'tu',
        'informatik': 'tu_marchstr',
        'architektur': 'tu_cafe_erp'}

def fetch(location='tu', veg=True, archive=None, cats=None):
    if not cats:
        cats = DEFAULT_CATS[location]

    res = requests.get('http://www.studentenwerk-berlin.de/speiseplan/rss/{}/woche/lang/{}'.format(location, int(veg)))

    if archive:
        fn = 'Mensa {} {}.rss'.format(location, datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
        with open(os.path.join(archive, fn), 'w+') as orig:
            orig.write(res.text)

    soup = bs4.BeautifulSoup(res.text, 'lxml')
    soup = bs4.BeautifulSoup(soup.find('item').find('description').text, 'lxml')

    format_shit = lambda el: [
            (f.find('strong').text + f.find(text=True, recursive=False), Decimal(f.find(class_='mensa_preise').text.split()[1]))
            for f in el.findAll(class_='mensa_speise')]

    ft = lambda key, name: [(name, format_shit(e)) for e in soup.findAll(class_=key)]

    stuff = [ft(*cat) for cat in cats]

    week = list(zip(*stuff))

    week = [[(n,[(m,p) for (m,p) in c if "Nudelauswahl" not in m or p != Decimal('2.45')]) for n,c in d] for d in week]

    return week

underline = lambda s, char='-': s + '\n' + (char*len(s))
WEEKDAYS = ('Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag')

def format_week(week):
    return '\n\n'.join( underline(weekday) + '\n' + format_day(day) for weekday,day in zip(WEEKDAYS, week) )

def format_cat(cat, stuff):
    return '~ {}scheiß ~\n'.format(cat) + ('\n'.join('{:<80} {:02f}'.format(meal, price)
            for meal, price in stuff) if stuff else 'Nix')

def format_day(day):
    return '\n'.join(format_cat(cat, stuff) for cat, stuff in day)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('location', default='tu', nargs='?')
    parser.add_argument('-V', '--vegetarian', action='store_true')
    parser.add_argument('-a', '--archive', help='Keep archival copy of source document under given path')
    args = parser.parse_args()

    loc = LOC_SHORTNAME_MAP.get(args.location, args.location)

    fd = fetch(loc, args.vegetarian, args.archive)
    print(format_week(fd))
