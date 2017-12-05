import re

regex = re.compile(r"([^:]*):(\d+):(\d*): {2}([^:]*):(.*)")

with open('results/flawfinder.txt', 'r') as f:
    for line in f.readlines():
        line = line.rstrip()
        m = regex.match(line)
        filename, lineno, colno, category, description = m.groups()
