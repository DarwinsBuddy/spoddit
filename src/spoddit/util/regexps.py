import re

_TRACK_REGEXPS = [
    # regex to match artist and title (most common form)
    r'(?P<artist>.+)\s+[^\s\w]{1}\s+(?P<title>.*)',
    # regex to match the whole string, if above form(s) are not applicable
    r'(?P<track>.+)'
]

COMBINED_TRACK_REGEX = re.compile(r'|'.join(_TRACK_REGEXPS))

# regex to get rid of those [Official something] tags
CLEANUP_REGEXPS = [
    re.compile(r'(?P<part1>.*)(\[.*\])(?P<part2>.*)'),
    re.compile(r'(?P<part1>.*)(\(.*\))(?P<part2>.*)'),
]

TRIM_REGEX = re.compile(r'[^\w]*(?P<trimmed>[\w\s]*(\s+[^\w]{1}\s+)[\s\w]*)[^\w]*')

# youtube
_YOUTUBE_REGEX = r'(?P<youtube>https:\/\/youtu\.be\/.*|https:\/\/www\.youtube\.com\/watch\?v\=.*)'
# spotify
_SPOTIFY_REGEX = r'(?P<spotify>https:\/\/open\.spotify\.com\/track\/.*)'
SPOTIFY_ID_REGEX = re.compile(r'https://open\.spotify\.com/track/(?P<spotify_id>[\w]*)\??')

# TODO: extend them for deezer, etc.
_MEDIA_LINK_REGEXPS = [
    _YOUTUBE_REGEX,
    _SPOTIFY_REGEX
]

COMBINED_MEDIA_LINK_REGEX = re.compile("|".join(_MEDIA_LINK_REGEXPS))

SUBREDDIT_REGEX = re.compile(r'r\/(.*)')
