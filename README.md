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

Set `PLAYLIST_NAME` and `RAW_END_DATE` in script then run it
`./newalbumrelease-spotify-playlists.py`

The script starts from now and runs to `RAW_END_DATE`
