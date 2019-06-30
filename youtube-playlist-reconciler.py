#!/usr/bin/env python

from utils.constants import cursor, colours
from client.youtube import youtube
import os
import sys
import argparse
import json
import glob
from collections import OrderedDict

PATH_CONFIG = "config"

# supplemented by cmdline args
config = None
extension = ".ytpl"
colourless = False
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


def diffs(list_):
    diffs = []
    local = set(list_["items"]["local"].keys()
                if "local" in list_["items"] else [])
    remote = set(list_["items"]["remote"].keys()
                 if "remote" in list_["items"] else [])
    added = (remote - local)
    added_count = len(added)
    if added_count > 0:
        list_["items"]["added"] = \
            [list_["items"]["remote"][id] for id in added]
        list_["items"]["added_count"] = added_count
        diffs.append("{0}added: {1}{2}".format(
            "" if colourless else colours.grn,
            {added_count},
            "" if colourless else colours.off))
    removed = (local - remote)
    removed_count = len(removed)
    if removed_count > 0:
        list_["items"]["removed"] = \
            [list_["items"]["local"][id] for id in removed]
        list_["items"]["removed_count"] = removed_count
        diffs.append("{0}removed: {1}{2}".format(
            "" if colourless else colours.red,
            {removed_count},
            "" if colourless else colours.off))
    return " | ".join(diffs)


def diffs_dump(list_):
    if "added_count" in list_["items"] and \
       list_["items"]["added_count"] > 0:
        print(f"  # added: {list_['items']['added_count']}")
        for item in list_["items"]["added"]:
            print(f"  [{item[0]}] {item[1]}")
    if "removed_count" in list_["items"] and \
       list_["items"]["removed_count"] > 0:
        print(f"  # removed: {list_['items']['removed_count']}")
        for item in list_["items"]["removed"]:
            print(f"  [{item[0]}] {item[1]}")


def display(lists, expand_state):
    print("playlists:")
    for list_ in lists.values():
        info = ""
        info += f"[{list_['id']}]"
        if not colourless:
            info += colours.hl
        info += f" '{list_['title']}'"
        if not colourless:
            info += colours.off
        if "local_count" in list_["items"] or \
           "remote_count" in list_["items"]:
            info += " | count(s): {0}|{1}".format(
                list_["items"]["local_count"]
                    if "local_count" in list_["items"] else "-",
                list_["items"]["remote_count"]
                    if "remote_count" in list_["items"] else "-")
        diffs_ = ""
        if "local" in list_["items"] or \
           "remote" in list_["items"]:
            diffs_ = diffs(list_)
            if len(diffs_) > 0:
                info += (" | " + diffs_)
        print(info)
        # expanded info
        if len(diffs_) > 0 and expand_state:
            diffs_dump(list_)


def rebuild(path):
    if not os.path.exists(path):
        print(f"[error] invalid list '{path}'")
        return 1
    lines = []
    with open(path) as f:
        lines = f.readlines()
    list_ = None
    count = 0
    for line in lines:
        o = json.loads(line)
        if line[0] != ' ':
            list_ = {"id": o[0], "title": o[1],
                     "items": {"local": OrderedDict()}}
        else:
            list_["items"]["local"][o[0]] = o
            count += 1
    list_["items"]["local_count"] = count

    return list_


def dump(lists, target):
    overwrite = 0
    for list_ in lists.values():
        lines = json.dumps([list_["id"], list_["title"]])
        lines += "\n  " + "\n  ".join([json.dumps(item) for item in
                                      list_["items"]["local"].values()])
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
            path = os.path.join(target, list_["title"] + extension)
            if os.path.exists(path) and overwrite == 0:
                while True:
                    sys.stdout.write(
                        f"[user] target '{list_['title']}' exists, " +
                        "[o]verwrite [a]ll, or [c]ancel? [o/a/c]:  ")
                    sys.stdout.write(cursor.left)
                    sys.stdout.flush()
                    res = sys.stdin.read(1).lower()
                    if res == "c":
                        return
                    if res == "o" or res == "a":
                        if res == "a":
                            overwrite = 1
                        break
                    # reset
                    sys.stdout.write(cursor.reset)
                    sys.stdout.flush()
            with open(path, "w") as f:
                f.write(lines)


def refresh(user, config):
    global lists

    yt = youtube(debug, config)

    playlists = []
    if debug > 0:
        print(f"[debug] retrieving playlists for user '{user}'")
    try:
        playlists = yt.get_playlists_by_user(user)
    except Exception as e:
        print("[error] playlist refresh failure, remote side issue")
        if debug > 0:
            print(str(e))

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
        lists[id]["items"]["remote"] = \
            OrderedDict({item[0]: item for item in items})
        lists[id]["items"]["remote_count"] = items_count


def run():
    global debug
    global lists

    user = ""
    target = ""

    config_read()
    if "api_key" not in config:
        raise Exception("[error] no 'api_key' entry found in config")
    if debug > 0:
        print(f"[debug] using developer api key: '{config['api_key']}'")
    if "user" in config:
        user = config["user"]

    parser = argparse.ArgumentParser(
        description='Youtube Playlist Reconciler')
    parser.add_argument(
        '-t', '--target', dest='target',
        type=str, nargs='?', const=".",
        help="path for local playlists set (default: '.')")
    parser.add_argument(
        '-r', '--refresh', dest='refresh', action='store_const',
        const=True, default=False,
        help="retrieve remote playlists set")
    parser.add_argument(
        '-u', '--user', dest='user',
        type=str, nargs='?', default="",
        help="youtube user to target in channel / playlists search")
    parser.add_argument(
        '-xs', '--expand-state', dest='expand_state', action='store_const',
        const=True, default=False,
        help="expand state information to show added / removed items")
    parser.add_argument(
        '-d', '--dump', dest='dump', action='store_const',
        const=True, default=False,
        help="dump local playlists to stdout")
    parser.add_argument(
        '-o', '--overwrite', dest='overwrite', action='store_const',
        const=True, default=False,
        help="overwrite local playlists set at target")
    parser.add_argument(
        '-nc', '--no-colour', dest='colourless', action='store_const',
        const=True, default=False,
        help="disable use of terminal colour escape codes")
    parser.add_argument(
        '-v', '--vebose', dest='verbose', action='store_const',
        const=True, default=False,
        help="enable verbose / debug output")
    args = parser.parse_args()

    # global switches
    global colourless
    colourless = args.colourless

    if not sys.argv[1:]:
        parser.print_help()
        exit(0)
    if args.verbose:
        debug = 1
    if args.target:
        # rebuild local set
        target = args.target
        for s in glob.glob(os.path.join(target, "*" + extension)):
            list_ = rebuild(s)
            if list_["id"] not in lists:
                lists[list_["id"]] = list_
            else:
                lists[list_["id"]]["items"]["local"] = list_["items"]["local"]

    if args.refresh:
        # pull remote set
        if len(args.user) > 0:
            if len(user) > 0 and debug > 0:
                print("[debug] overriding config user..")
        if len(user) == 0:
            raise Exception("[error] no 'user' set")
        if debug > 0:
            print(f"[debug] using user: '{user}'")
        refresh(user, config)

    if args.dump:
        # write local set
        for id, list_ in lists.items():
            if "local" not in list_["items"] or \
               (args.overwrite and "remote" in list_["items"]):
                list_["items"]["local"] = list_["items"]["remote"]
                list_["items"]["local_count"] = list_["items"]["remote_count"]
        dump(lists, target if (target and args.overwrite) else "-")

    # default
    if not args.dump:
        display(lists, args.expand_state)


if __name__ == '__main__':
    run()
