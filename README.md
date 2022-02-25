# GENIUS LYRICS SCRAPER

---

## Usage

First, generate a keys.json file with your Genius API keys. It should look like this:

```json
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "access_token": "YOUR_ACCESS_TOKEN_HERE"
}
```

With your keys.json in the same directory that you're running your script, you can use GeniusRetriever like so:

```python
g = GeniusRetriever()

num_songs_to_get = 30
artists = ["Charli XCX", "A. G. Cook", "100 gecs"]

g.get_song_lyrics_from_artists(artists, num_songs_to_get)

g.write_lyrics("lyrics.txt")
```
