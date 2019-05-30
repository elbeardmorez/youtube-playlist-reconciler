#!/usr/bin/env python

from client.youtube import youtube
import os
import json

PATH_CONFIG = "config"

# supplemented by cmdline args
config = None
debug = 1

def config_read():
    global config
    if not os.path.exists(PATH_CONFIG):
        config = {}
        return
    with open(PATH_CONFIG) as f_config:
        config = json.load(f_config)


def run():
    global debug

    config_read()
    if "api_key" not in config:
        raise Exception("[error] no 'api_key' entry found in config")
    if debug > 0:
        print(f"[debug] using developer api key: '{config['api_key']}'")
    if "user" not in config:
        raise Exception("[error] no 'user' entry found in config")
    if debug > 0:
        print(f"[debug] using user: '{config['user']}'")
    user = config["user"]

    yt = youtube(debug)

    if debug > 0:
        print(f"[debug] retrieving playlists for user '{user}'")
    playlists = yt.get_playlists_by_user(user, config)
    for playlist in playlists:
        if debug > 0:
            print(f"[debug] retrieving playlist '{playlist[1]}' entries")
        items = yt.get_playlists_data(playlist[0])
        items_count = len(items)
        if debug > 0:
            print(f"[debug] playlist '{playlist[0]}' contains {items_count}" +
                  f" item{'' if items_count != 1 else 's'}")
            if items_count > 0:
                print("  " + "\n  ".join([json.dumps(item)
                                          for item in items]))

if __name__ == '__main__':
    run()
