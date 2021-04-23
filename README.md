Summary
---
Creates Spotify playlists from the newalbumreleases.net website

Creates a whitelist playlist for genres known to be liked and creates a
graylist playlist for lesser liked genres.  A blacklist prevents unliked
genres from being in any playlist.  Genres not in any list are outputted
at the end.

Blacklist of words from albums to prevent Best Ofs, Live, etc albums from
being included.  These albums are outputted at the end for verification.

Setup
---

Create a config file in config.yaml like below
```
username: ""
client_id: ""
client_secret: ""
playlist_id: ""
redirect_uri: ""
```

Fill in values following Spotify setup instructions:
https://spotipy.readthedocs.io/en/2.16.1/#getting-started

Install dependencies
`pip install -r requirements.txt`

Create a `config.properties` file like below and set `PLAYLIST_NAME` and `RAW_END_DATE`
```
[Main_Section]
PLAYLIST_NAME=fixme-2021-04-23
# Script starts at INDEX_START and then goes back in time till it hits this date
RAW_END_DATE=Tue, 16 Apr 2021 00:00:00 +0000
# Only change this if wanting to start at a different point in time than now
INDEX_START=1
# INDEX_START = 41  # could be November
# INDEX_START = 90  # could be October
# INDEX_START = 141  # could be September
# INDEX_START = 179  # could be August
# INDEX_START = 214  # could be July
```

Run the script
`./newalbumrelease-spotify-playlists.py`

The script starts from `INDEX_START` and runs to `RAW_END_DATE`
