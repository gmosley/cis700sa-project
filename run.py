import plistlib
from collections import defaultdict
import pygments
from pygments import highlight
from pygments.lexers import CLexer
from pygments.formatters import HtmlFormatter
import re
import json
import pprint
import sys
import subprocess
import glob
import os

if len(sys.argv) != 2:
    print('usage python3 run.py <source.c>')
    exit(1)

source_input = sys.argv[1]

# run each tool on the source code
subprocess.run(['./analyze.sh', source_input])

# add tool outputs if they exist
tool_outputs = []

if os.path.isfile('results/flawfinder.txt'):
    tool_outputs.append(('flawfinder', 'results/flawfinder.txt'))

cppcheck_glob = glob.glob('results/cppcheck/*.plist')
if len(cppcheck_glob) == 1:
    tool_outputs.append(('cppcheck', cppcheck_glob[0]))

scanbuild_glob = glob.glob('results/scan-build/*/*.plist')
if len(cppcheck_glob) == 1:
    tool_outputs.append(('scan-build', scanbuild_glob[0]))

if os.path.isfile('results/infer/report.json'):
    tool_outputs.append(('infer', 'results/infer/report.json'))


tool_reports = defaultdict(list)


def parse_plist(tool, report_file):
    with open(report_file, 'rb') as f:
        p = plistlib.load(f, fmt=plistlib.FMT_XML)
    for d in p['diagnostics']:
        mesg = '{}: ({} {}) {}'.format(
            tool,
            d['category'],
            d['check_name'],
            d['description']
        )
        location = d['location']
        tool_reports[location['line']].append(mesg)


def parse_flawfinder(tool, report_file):
    flawfinder_regex = re.compile(r"([^:]*):(\d+):(\d*): {2}(\[\d\])([^:]*):(.*)")
    with open(report_file, 'r') as f:
        for line in f.readlines():
            line = line.rstrip()
            m = flawfinder_regex.match(line)
            filename, lineno, colno, category, check_name, description = m.groups()
            mesg = '{}: ({} {}) {}'.format(
                tool,
                category,
                check_name,
                description
            )
            tool_reports[int(lineno)].append(mesg)


def parse_infer(tool, report_file):
    with open(report_file, 'r') as f:
        results = json.load(f)
        for result in results:
            mesg = '{}: ({} {}) {}'.format(
                tool,
                result['severity'],
                result['bug_type_hum'],
                result['qualifier']
            )
            tool_reports[result['line']].append(mesg)


for tool, report_file in tool_outputs:
    if tool is 'flawfinder':
        parse_flawfinder(tool, report_file)
    elif tool in ['cppcheck', 'scan-build']:
        parse_plist(tool, report_file)
    elif tool is 'infer':
        parse_infer(tool, report_file)
    else:
        print('unknown tool: ' + tool)
        exit(1)

with open(source_input, 'r') as f:
    source_data = f.read()

pprint.pprint(tool_reports)

# use a custom formatter so we have more control
# right now just using it to guarantee each stylized line directly maps to a source line
class CodeHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            yield i, t


with open('combined-report.html', 'w') as f:
    f.write('<!DOCTYPE html>\n<html>\n<head>\n<style>\n')
    f.write(HtmlFormatter().get_style_defs('.highlight'))
    f.write('\n.result { color: #F03434 }\n')
    f.write('</style>\n</head>\n<body>\n')

    # needed for syntax highlighting
    f.write('<div class="highlight"><pre>\n')

    formatted_html = pygments.highlight(source_data, CLexer(), CodeHtmlFormatter())
    for lineno, line in enumerate(formatted_html.split('\n'), 1):
        f.write('{:3} '.format(lineno) + line + '\n')

        if lineno in tool_reports:
            for special_line in tool_reports[lineno]:
                f.write('<span class=\"result\">    > {}</span>\n'.format(special_line))

    # close syntax highlighting
    f.write('</pre></div>\n')

    f.write('</body>\n</html>\n')