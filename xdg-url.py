#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse,subprocess,re
from pathlib import Path

parser = argparse.ArgumentParser(description="xdg-url")
parser.add_argument('path')
args = parser.parse_args()

with Path(args.path).open("r") as f:
  for l in f.readlines():
    m = re.match('(URL=)?([a-z]*:\/\/.*)',l)
    if m:
      subprocess.Popen(["xdg-open",m.group(2)])