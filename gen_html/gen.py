# This is a very rough prototype to generate html files containg the reports from all files

import plistlib
from collections import defaultdict
import pygments
from pygments import highlight
from pygments.lexers import CLexer
from pygments.formatters import HtmlFormatter

# TODO: don't hard code
source_input = 'source.c'
tool_inputs = [('cppcheck', 'cppcheck.plist'),
               ('scan-build', 'scan-build.plist')]

tool_reports = defaultdict(list)

for tool, report_file in tool_inputs:
    with open(report_file, 'rb') as f:
        p = plistlib.load(f, fmt=plistlib.FMT_XML)
        for d in p['diagnostics']:
            mesg = '{}: {} {}'.format(
                tool,
                d['category'],
                d['description']
            )
            location = d['location']
            tool_reports[location['line']].append(mesg)

with open(source_input, 'r') as f:
    source_data = f.read()

# use a custom formatter so we have more control
# right now just using it to guarantee each stylized line directly maps to a source line
class CodeHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            yield i, t


with open('source.html', 'w') as f:
    f.write('<!DOCTYPE html>\n<html>\n<head>\n<style>\n')
    f.write(HtmlFormatter().get_style_defs('.highlight'))
    f.write('\n</style>\n</head>\n<body>\n')

    # needed for syntax highlighting
    f.write('<div class="highlight"><pre>\n')

    formatted_html = pygments.highlight(source_data, CLexer(), CodeHtmlFormatter())
    for lineno, line in enumerate(formatted_html.split('\n'), 1):
        f.write('{:3} '.format(lineno) + line + '\n')

        if lineno in tool_reports:
            for special_line in tool_reports[lineno]:
                f.write('    --> ' + special_line + '\n')

    # close syntax highlighting
    f.write('</pre></div>\n')

    f.write('</body>\n</html>\n')