import re

regex = re.compile(r"([^:]*):(\d+):(\d*): {2}(\[\d\])([^:]*):(.*)")

with open('results/flawfinder.txt', 'r') as f:
    for line in f.readlines():
        line = line.rstrip()
        m = regex.match(line)
        filename, lineno, colno, category, check_name, description = m.groups()
