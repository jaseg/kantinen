#!/usr/bin/env python3

import tempfile, requests, subprocess, re, argparse
from datetime import datetime
from decimal import Decimal
from contextlib import contextmanager
import os.path

def fetch(location='MA', archive=None):
    @contextmanager
    def afile():
        if archive:
            fn = 'Kantine {} {}.pdf'.format(location, datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
            yield open(os.path.join(archive, fn), 'w+b')
        else:
            yield tempfile.NamedTemporaryFile()

    with afile() as orig:
        res = requests.get('http://personalkantine.personalabteilung.tu-berlin.de/pdf/{}-aktuell.pdf'.format(location))
        orig.write(res.content)
        with tempfile.NamedTemporaryFile() as out:
            subprocess.check_output(['pdfcrop', '--margins', '-80 -160 -60 -140', orig.name, out.name])
            c = subprocess.check_output(['venv2/bin/pdf2txt.py', '-p', '1', out.name]).decode('UTF-8')

    l = re.split('Montag|Dienstag|Mittwoch|Donnerstag|Freitag', c)[3:]

    res = (('^\W*[,.]?\W*([0-9. ]{4,9})?\W*', ''),
           ('“\W*([^“]*\w)\W*“', '“\\1“'),
           ('\\(\W*', '('),
           ('\W*\\)', ')'),
           (' ([a-zäöüß]) ', '\\1'),
           ('\s+', ' '),
           ('\s*([-/])\s*', '\\1'))

    def subs(s):
        for pat,repl in res:
            s = re.sub(pat, repl, s)
        return s

    e = [[ subs(v).strip() for v in vs if not 'Jodsalz' in v and v.strip()] for vs in [e.split('€') for e in l]]
    f = [[(' '.join(title), Decimal(price.replace(',', '.'))) for *title, price in [el.split() for el in k]] for k in e]
    return f

def print_week(week):
    for i,day in enumerate(week):
        print(('Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag')[i])
        print('--------');
        for meal, price in day:
            print('{:<80} {:02f}'.format(meal, price))
        print()

parser = argparse.ArgumentParser()
parser.add_argument('location', default='MA', nargs='?')
parser.add_argument('-a', '--archive', help='Keep archival copy of source document under given path')
args = parser.parse_args()

print_week(fetch(args.location, args.archive))
