from ast import Index
import sys
import json
import requests as r
from urllib.parse import quote as encode
from bs4 import BeautifulSoup as bsp
import multiprocessing as mp

base_url = "https://api.genius.com/"


class GeniusRetriever:
    def __init__(self, keys: dict = None) -> None:
        if not keys:
            self.keys = self.get_keys()
        else:
            self.keys = keys
        self.access = self.keys["access_token"]
        self.auth_header = {"Authorization": "Bearer " + self.access}
        self.request_count = 0
        self.text = ""
        self.pool_max = 10
        self.lock = mp.Lock()

    def get_keys(self):
        with open("keys.json") as f:
            keys = json.load(f)
        return keys

    @staticmethod
    def search_artist_id_static(artist_name, auth_header):
        url = base_url + "search"
        params = {"q": artist_name}
        response = r.get(url, params=params, headers=auth_header)
        artist_api_path = response.json()["response"]["hits"][0]["result"][
            "primary_artist"
        ]["api_path"]
        return artist_api_path.split("/")[-1]

    def search_artist_id(self, artist_name):
        return self.search_artist_id_static(artist_name, self.auth_header)

    @staticmethod
    def get_lyrics_url(songs_id):
        url_norm = "https://genius.com"
        url = url_norm + "/songs/" + songs_id
        return url

    @staticmethod
    def get_song_lyrics(song_url, song_title):
        response = r.get(song_url)
        html = bsp(response.text, "html.parser")
        lyrics_els = html.find_all("div", attrs={"data-lyrics-container": "true"})
        lyrics = song_title + "\n"
        for el in lyrics_els:
            for br in el.find_all("br"):
                br.replace_with("\n")
            lyrics += el.get_text() + "\n"

        return lyrics

    def get_song_lyrics_from_artist(self, artist_id, hits: bool):
        url = base_url + "artists/" + encode(artist_id) + "/songs"
        params = {"per_page": self.pool_max, "sort": "popularity" if hits else "title"}
        response = r.get(url, params=params, headers=self.auth_header)
        song_response = response.json()["response"]["songs"]
        song_urls = [(p["url"], p["title"]) for p in song_response]
        with mp.Pool(self.pool_max) as p:
            lyrics_list = p.starmap(self.get_song_lyrics, song_urls)
        lyrics = "\n\n\n".join(lyrics_list) + "\n\n\n"
        self.lock.acquire()
        self.text += lyrics
        self.lock.release()
        return lyrics

    def get_song_lyrics_from_artists(self, artists, per_artist=25, hits=True):
        self.pool_max = per_artist
        get_id_args = [(artist, self.auth_header) for artist in artists]
        with mp.Pool(self.pool_max) as p:
            artists_ids = p.starmap(self.search_artist_id_static, get_id_args)
        for id in artists_ids:
            self.get_song_lyrics_from_artist(id, hits=hits)

    def write_lyrics(self, outfile):
        with open(outfile, "w") as f:
            f.write(self.text)

    def get_lyrics_as_str(self):
        return self.text


if __name__ == "__main__":
    g = GeniusRetriever()
    try:
        outfile = sys.argv[1]
    except IndexError:
        outfile = "lyrics.txt"
    artists = ["Charli XCX", "A. G. Cook", "100 gecs"]
    g.get_song_lyrics_from_artists(artists, 30)
    g.write_lyrics(outfile)
