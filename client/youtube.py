
from googleapiclient.discovery import build
import json

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
RESULTS_PER_PAGE = 50  # max


class youtube:

    version = "0.0.1"
    service = None
    debug = 0

    def __init__(self, debug=0, config=None):
        self.debug = debug
        self.initialise_service(config)

    def get_info(self):
        return {"version": self.version}

    def initialise_service(self, config):
        if config:
            if self.service:
                self.service = None
            if "api_key" not in config:
                raise Exception("[error] no api key provided")

            if self.debug > 0:
                print("[debug] building service")
            self.service = build(API_SERVICE_NAME,
                                 API_VERSION,
                                 developerKey=config["api_key"])
            if self.debug > 0 and self.service:
                print("[debug] youtube service initialised")

        if not self.service:
            raise Exception("[error] no service available")

    def get_playlists_by_channel(self, channel, config=None):
        self.initialise_service(config)
        data = self.service.playlists().list(
                  part="id,snippet", channelId=channel,
                  fields="items(id,snippet/title)",
                  maxResults=RESULTS_PER_PAGE).execute()
        playlists = [[item["id"], bytes.decode(
                        str.encode(item["snippet"]["title"], "utf8"),
                        "utf8")] for item in data["items"]]
        playlists_count = len(playlists)
        if self.debug > 0:
            print(f"[debug] search found {playlists_count} playlist" +
                  f"{'' if playlists_count == 1 else 's'} for '{channel}'")
            if playlists_count > 0:
                print("  " + "\n  ".join([json.dumps(playlist)
                                          for playlist in playlists]))
        return playlists

    def get_playlists_by_user(self, user, config=None):
        self.initialise_service(config)

        playlists = []
        data = self.service.search().list(
                  part="id", type="channel", q=user,
                  maxResults=RESULTS_PER_PAGE).execute()
        channels = [item["id"]["channelId"] for item in data["items"]]
        channels_count = len(channels)
        if self.debug > 0:
            print(f"[debug] found {channels_count} channel" +
                  f"{'' if channels_count == 1 else 's'} for '{user}'")
            if channels_count > 0:
                print("  " + "\n  ".join(channels))
        if channels_count == 0:
            return playlists

        for channel in channels:
            playlists += self.get_playlists_by_channel(channel)

        return playlists

    def get_playlists_data(self, playlist, config=None):
        self.initialise_service(config)

        nextPageToken = ""
        items = []
        total_results = 1
        while len(items) < total_results:
            data = self.service.playlistItems().list(
                        part="id,snippet",
                        playlistId=playlist,
                        fields="items(snippet(title,resourceId(videoId)))," +
                               "nextPageToken,pageInfo(totalResults)",
                        maxResults=RESULTS_PER_PAGE,
                        pageToken=nextPageToken).execute()
            items += data["items"]
            total_results = data["pageInfo"]["totalResults"]
            if "nextPageToken" in data:
                nextPageToken = data["nextPageToken"]

        items = [[item["snippet"]["resourceId"]["videoId"],
                  bytes.decode(
                      str.encode(item["snippet"]["title"], 'utf8'),
                      "utf8")] for item in items]
        return items
