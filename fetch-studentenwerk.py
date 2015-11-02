#!/usr/bin/env python3

import bs4, requests, argparse
from decimal import Decimal
from datetime import datetime
import os.path


def fetch(location='tu', veg=True, archive=None):
    res = requests.get('http://www.studentenwerk-berlin.de/speiseplan/rss/{}/woche/lang/{}'.format(location, int(veg)))
    if archive:
        fn = 'Mensa {} {}.rss'.format(location, datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
        with open(os.path.join(archive, fn), 'w+') as orig:
            orig.write(res.text)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    soup = bs4.BeautifulSoup(soup.find('item').find('description').text, 'lxml')

    format_shit = lambda el: [
            (f.find('strong').text, Decimal(f.find(class_='mensa_preise').text.split()[1]))
            for f in el.findAll(class_='mensa_speise')]

    ft = lambda t: [format_shit(e) for e in soup.findAll(class_=t)]

    special, food, soups = map(ft, ('special', 'food', 'soups'))

    week = list(zip(special, food, soups))

    return week

def print_week(week):
    for i,(a,b,c) in enumerate(week):
        print(('Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag')[i])
        print('--------');
        print('~ Special shit ~')
        for meal, price in a:
            print('{:<80} {:02f}'.format(meal, price))
        print()
        print('~ Ordinary shit ~')
        for meal, price in b:
            print('{:<80} {:02f}'.format(meal, price))
        print()
        print('~ Soup shit ~')
        for meal, price in c:
            print('{:<80} {:02f}'.format(meal, price))
        print()

parser = argparse.ArgumentParser()
parser.add_argument('location', default='tu', nargs='?')
parser.add_argument('-V', '--vegetarian', action='store_true')
parser.add_argument('-a', '--archive', help='Keep archival copy of source document under given path')
args = parser.parse_args()

print_week(fetch(args.location, args.vegetarian, args.archive))
