# youtube-playlist-reconciler

## description
dump your youtube playlists

## usage
- acquire a google apis developer key
- copy `config.sample` to `config` and update its content
- run the script
```
usage: youtube-playlist-reconciler.py [-h] [-u [USER]] [-d] [-t [TARGET]] [-v]

Youtube Playlist Reconciler

optional arguments:
  -h, --help            show this help message and exit
  -u [USER], --user [USER]
                        youtube user to target
  -d, --dump            dump remote playlists
  -t [TARGET], --target [TARGET]
                        target path for local lists (default: stdout)
  -v, --vebose          enable verbose / debug output
```

## examples
```
  $ ./youtube-playlist-reconciler > lists

  $ ./youtube-playlist-reconciler --user tube69 --dump --target path/to/lists

```
## resources
https://github.com/youtube/api-samples

https://developers.google.com/youtube/v3/docs/channels/list
https://developers.google.com/youtube/v3/docs/channels#properties

https://developers.google.com/youtube/v3/docs/playlists/list
https://developers.google.com/youtube/v3/docs/playlists#properties

https://developers.google.com/youtube/v3/docs/playlistItems#properties
