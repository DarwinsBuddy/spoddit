
# spoddit

A reddit scraper for music with spotify integration

# Usage

1. Install venv
2. `. venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cd src/ && python -m spoddit`

# Configuration

## `.secrets.conf`

### `[Spotify]`
* `CLIENT_ID` client id of our spotify application
* `CLIENT_SECRET` client secret of our spotify application

### `[Reddit]`
* `CLIENT_ID`  client id of our reddit application

## `spoddit.conf`

### `[Spotify]`
* `username` Your username, which you want to be authenticated with

### `[General]`
* `port` Used for OAuth2 redirect. If the specified port doesn't work out for you, simply change it to another spare one on your system.
> Note: This port will only be used temporarily, while authenticating against the Spotify API.

### `[r/<SOME_SUBREDDIT>]`
> Note: For every section in this config file starting with `r/`, you will create a scrape job for the eponymous subreddit. Below options allow you to configure this. e.g. where the scraped music goes, e.g. how much is getting scraped, etc.
* `playlist_name` name of the playlist going to be extended by scraped tracks of this subreddit
* `limit` = `50` How many submissions from `hot` are being scraped
* `public` True/False Whether or not the playlist should be public or not
* `description` A user defined description for this playlist

## `log.conf`
Python logger configuration. See [python logging config file format](https://docs.python.org/3/library/logging.config.html#logging-config-fileformat)
for more details.

# License
© Christoph Spörk 2020
As for now I'll go with GNU GPL v3, but I am not sure yet.