# youtube-playlist-reconciler

## description
dump your youtube playlists locally, then periodically compare remote and local sets, updating / overwriting locally when you're 'happy' (aka. after you've search youtube for suitable replacements to the automatically deleted videos). at least with this 'tool' you'll know which were deleted!

## usage
- acquire a google apis developer key [here](https://console.developers.google.com/)
- copy `config.sample` to `config` and update its content
- run the script
```
usage: youtube-playlist-reconciler.py [-h] [-t [TARGET]] [-r] [-u [USER]]
                                      [-xs] [-d] [-o] [-v]

Youtube Playlist Reconciler

optional arguments:
  -h, --help            show this help message and exit
  -t [TARGET], --target [TARGET]
                        path for local playlists set (default: '.')
  -r, --refresh         retrieve remote playlists set
  -u [USER], --user [USER]
                        youtube user to target in channel / playlists search
  -xs, --expand-state   expand state information to show added / removed items
  -d, --dump            dump local playlists to stdout
  -o, --overwrite       overwrite local playlists set at target
  -v, --vebose          enable verbose / debug output
```

## examples

### list local playlist set (useful for counts only)
```sh
  $ ./youtube-playlist-reconciler -t
```
```
  playlists:
  [PL88rnnizU2vjUw5rB9p4S9zqKdCkE3gpG] | documentaries | count(s): 17|-
```
### list local / remote playlist sets (useful for diff status)
```sh
  $ ./youtube-playlist-reconciler --target local/path --remote --user tube69
```
```
  playlists:
  [PL88rnnizU2vjUw5rB9p4S9zqKdCkE3gpG] | documentaries | count(s): 17|18 | added: 1
``` 
 ### reveal local / remote playlist set differences
```sh
  $ ./youtube-playlist-reconciler --target local/path --remote --user tube69 --expand-state
```
```
  playlists:
  [PL88rnnizU2vjUw5rB9p4S9zqKdCkE3gpG] | documentaries | count(s): 17|18 | added: 1
    # added: 1
    [X5uGLbV5zVo] The Money Myth: Jem Bendell at TEDxTransmedia2011
```

### update local playlist sets with remote playlist sets
```sh
  $ ./youtube-playlist-reconciler --target local/path --remote --user tube69 --dump --overwrite
  $ ./youtube-playlist-reconciler --target local/path
```
```
  playlists:
  [PL88rnnizU2vjUw5rB9p4S9zqKdCkE3gpG] | documentaries | count(s): 18|-
```

## implementation
the aim is simply synchronisation, following reconciliation (by way of diffs and manual online intervention), of local and remote playlists. the local set is (re)built when the `--target` option is used, and the remote set is retrieved and built when the `--remote` option is used. comparison is performed via maps (dictionary data structures) keyed on item ids (where both sets are opted for / built)

the default output is the list of playlists and their 'state' (summary of differences). the `--expand-state` option reveals these differences, and finally, the combination of `--dump` and `--overwrite` options can be used to persist the (**externally** fixed / corrected) remote lists

## resources
https://github.com/youtube/api-samples

https://developers.google.com/youtube/v3/docs/channels/list
https://developers.google.com/youtube/v3/docs/channels#properties

https://developers.google.com/youtube/v3/docs/playlists/list
https://developers.google.com/youtube/v3/docs/playlists#properties

https://developers.google.com/youtube/v3/docs/playlistItems#properties
