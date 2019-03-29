"""Test our ability to parse ISO8601 timestamps"""

from guano import parse_timestamp

fmts = [
    '2016-12-10T01:02:03',
    '2016-12-10T01:02:03.123',
    '2016-12-10T01:02:03.123456',

    '2016-12-10T01:02:03Z',
    '2016-12-10T01:02:03.123Z',
    '2016-12-10T01:02:03.123456Z',

    '2016-12-10T01:02:03-07:00',
    '2016-12-10T01:02:03.123-07:00',
    '2016-12-10T01:02:03.123456-07:00',

    '2016-12-10 01:02:03',  # bonus
]

for fmt in fmts:
    print fmt, '\t', len(fmt), '\t', parse_timestamp(fmt), '\t', parse_timestamp(fmt).isoformat()
