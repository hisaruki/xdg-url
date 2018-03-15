#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import json
import furl
import tempfile
import requests
import hashlib
import datetime
from pathlib import Path
from collections import Counter

urls = []

applications = (
    Path().home() / Path(".local/share/applications/xdg-chrome-bookmark"))
try:
    applications.mkdir()
except:
    ""
try:
    (applications/Path("favicons")).mkdir()
except:
    ""

for p in applications.glob("**/*"):
    if not p.is_dir():
        p.unlink()


with tempfile.NamedTemporaryFile(delete=True) as tf:
    with (Path().home() / Path(".config/google-chrome/Default/Favicons")).open("rb") as f:
        tf.write(f.read())
        conn = sqlite3.connect(tf.name)
        c = conn.cursor()

bookmarks = []


def walk(d):
    if type(d) == dict:
        for v in d.values():
            if type(v) == dict:
                walk(v)
            else:
                if type(v) == list:
                    walk(v)
    elif type(d) == list:
        for i in d:
            if not "url" in i:
                walk(i)
            else:
                bookmarks.append(i)


with (Path().home() / Path(".config/google-chrome/Default/Bookmarks")).open("r") as f:
    walk(json.loads(f.read()))

def mkdesktop(bookmark):
    scheme = furl.furl(bookmark["url"]).scheme
    if scheme == "http" or scheme == "https":
        sql = 'SELECT icon_id FROM icon_mapping WHERE page_url = "' + \
            bookmark["url"]+'";'
        f = c.execute(sql).fetchone()
        if f:
            favicon_id = str(max(list(f)))
            sql = 'SELECT url FROM favicons WHERE id = '+favicon_id+';'
            f = c.execute(sql).fetchone()
            if f:
                favicon_url = f[0].replace("made-up-favicon:", "")
                favicon = (applications/Path("favicons")/bookmark["id"])
                if not favicon.exists():
                    try:
                        r = requests.get(favicon_url)
                        with favicon.open("wb") as f:
                            f.write(r.content)
                    except:
                        ""
                if favicon.exists():
                    bookmark["favicon"] = str(favicon)

    result = '''[Desktop Entry]
Version=1.0
Terminal=false
Type=Application
Categories=Network;WebBrowser;
'''
    result += 'Name='+bookmark["name"]+" "+bookmark["url"]+"\n"
    result += 'Exec=xdg-open '+bookmark["url"]+"\n"
    if "favicon" in bookmark:
        result += 'Icon='+bookmark["favicon"]+"\n"
    desktop = (Path(applications) / Path(bookmark["id"]+".desktop"))
    with desktop.open("w") as f:
        f.write(result)
    urls.append(bookmark["url"])

for bookmark in bookmarks:
    try:
        microseconds = int(bookmark["meta_info"]["last_visited_desktop"])
    except:
        try:
            microseconds = int(bookmark["meta_info"]["last_visited"])
        except:
            microseconds = None
    if microseconds:
        seconds, microseconds = divmod(microseconds, 1000000)
        days, seconds = divmod(seconds, 86400)
        dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, microseconds)
        if (datetime.datetime.now() - dt).days < 8:
            mkdesktop(bookmark)

with tempfile.NamedTemporaryFile(delete=True) as tf:
    with (Path().home() / Path(".config/google-chrome/Default/Top Sites")).open("rb") as f:
        tf.write(f.read())
        conn = sqlite3.connect(tf.name)
        c = conn.cursor()

sql = 'SELECT url, title, thumbnail from thumbnails;'
for url, title, thumbnail in c.execute(sql):
    if not url in urls:
        result = '''[Desktop Entry]
    Version=1.0
    Terminal=false
    Type=Application
    Categories=Network;WebBrowser;
    '''
        result += 'Name='+title+" "+url+"\n"
        result += 'Exec=xdg-open '+url+"\n"
        desktop = (Path(applications) / Path(title.lstrip().rstrip()+".desktop"))
        with desktop.open("w") as f:
            f.write(result)