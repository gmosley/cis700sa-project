import plistlib
import pprint
import sys

with open(sys.argv[1], 'rb') as f:
    p = plistlib.load(f, fmt=plistlib.FMT_XML)

files = p['files']
version = p['clang_version']

print(version)

for d in p['diagnostics']:
    # clang only (empty in cppcheck):
    #   * HTMLDiagnostics_files
    #   * issue_context
    #   * issue_context_kind

    # both have a path field that shows the path of the bug

    location = d['location']
    print('{}:{}:{} ({}) {}'.format(
        files[location['file']],
        location['line'],
        location['col'],
        d['category'],
        d['description']))
