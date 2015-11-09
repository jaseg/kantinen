#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import fetch_gutmann as gm
import fetch_studentenwerk as sw

SERVER      = 'mail.physik.tu-berlin.de'
FROM_ADDR   = 'foodbot@physik.tu-berlin.de'
TO_ADDR     = 'essen-l@lists.physik.tu-berlin.de'


dt = datetime.now()
if dt.hour >= 18:
    dt += timedelta(days=1)
wd = dt.weekday()

format_plan = lambda name, stuff: gm.underline(name, char='=') +'\n'+ stuff

plans = [
    format_plan('Mathekantine',         gm.format_day(gm.fetch('MA', 'archive')[wd])),
    format_plan('Hauptmensa',           sw.format_day(sw.fetch('tu', False, 'archive')[wd])),
    format_plan('Informatik-Cafeteria', sw.format_day(sw.fetch('tu_marchstr', False, 'archive')[wd])),
    format_plan('EN-Cafete',            gm.format_day(gm.fetch('EN', 'archive')[wd])),
    format_plan('Architektur',          sw.format_day(sw.fetch('tu_cafe_erp', False, 'archive')[wd])),
    format_plan('Skyline',              sw.format_day(sw.fetch('tu_cafe_skyline', False, 'archive')[wd]))
    ]

subject = 'Speisepläne für {weekday}, {date}'.format(weekday=gm.WEEKDAYS[wd], date=dt.date())

msg = MIMEText('\n\n'.join([subject] + plans))
msg['Subject']  = subject
msg['From']     = FROM_ADDR
msg['To']       = TO_ADDR

srv = smtplib.SMTP_SSL(SERVER, 465)
#srv.set_debuglevel(1)
srv.send_message(msg)
srv.quit()
