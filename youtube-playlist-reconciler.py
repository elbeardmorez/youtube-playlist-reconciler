#!/usr/bin/env python

from client.youtube import youtube
import os
import sys
import argparse
import json

PATH_CONFIG = "config"

# supplemented by cmdline args
config = None
debug = 0

# state
lists = {}


def config_read():
    global config
    if not os.path.exists(PATH_CONFIG):
        config = {}
        return
    with open(PATH_CONFIG) as f_config:
        config = json.load(f_config)


def dump_list(list_, target):
    lines = json.dumps([list_["id"], list_["title"]])
    lines += "  " + "\n  ".join([json.dumps(item)
                                 for item in list_["items"]["local"]])
    if target == "-":
        # stdout
        print(lines)
    else:
        if not os.path.exists(target):
            try:
                os.mkdir(target)
            except Exception as e:
                raise Exception(
                    "[error] couldn't make target directory" +
                    f"{target} :\n" + str(e))
        path = os.path.join(target, list_["title"])
        with open(path, "w") as f:
            f.write(lines)


def refresh(user, config):
    global lists

    yt = youtube(debug, config)

    if debug > 0:
        print(f"[debug] retrieving playlists for user '{user}'")
    playlists = yt.get_playlists_by_user(user)
    for playlist in playlists:
        id = playlist[0]
        title = playlist[1]
        if debug > 0:
            print(f"[debug] retrieving playlist '{title}' entries")
        items = yt.get_playlists_data(id)
        items_count = len(items)
        if debug > 0:
            print(f"[debug] playlist '{id}' contains {items_count}" +
                  f" item{'' if items_count == 1 else 's'}")
        # add / update lists state for upstream
        if id not in lists:
            if debug > 0:
                print("[debug] adding playlist to state")
            lists[id] = {}
            lists[id]["id"] = id
            lists[id]["items"] = {}
        lists[id]["title"] = title
        lists[id]["items"]["remote"] = items
        lists[id]["items"]["remote_count"] = items_count


def run():
    global debug
    global lists

    target = "-"

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

    parser = argparse.ArgumentParser(
        description='Youtube Playlist Reconciler')
    parser.add_argument(
        '-d', '--dump', dest='dump', action='store_const',
        const=True, default=False,
        help="dump remote playlists")
    parser.add_argument(
        '-t', '--target', dest='target',
        type=str, nargs='?', const=".",
        help="target path for local lists (default: '.')")
    parser.add_argument(
        '-v', '--vebose', dest='verbose', action='store_const',
        const=True, default=False,
        help="enable verbose / debug output")
    args = parser.parse_args()

    if not sys.argv[1:]:
        parser.print_help()
        exit(0)
    if args.verbose:
        debug = 1

    if args.dump:
        if args.target:
            target = args.target
        refresh(user, config)
        for id, list_ in lists.items():
            if "local" not in list_["items"]:
                list_["items"]["local"] = list_["items"]["remote"]
                list_["items"]["local_count"] = list_["items"]["remote_count"]
            dump_list(list_, target if target else "-")


if __name__ == '__main__':
    run()
