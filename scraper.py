import json
import urllib.request

class SongCollection:

    def get_lyrics(self, artist, song):
        artist = artist.replace(" ", "%20")
        song = song.replace(" ", "%20")

        data = json.load(urllib.request.urlopen('http://lyric-api.herokuapp.com/api/find/{}/{}'.format(artist, song)))

        return data["lyric"]


def main():
    data = json.load(urllib.request.urlopen())
    print(data['lyric'])
    print(str(data['lyric']).split())

if __name__ == "__main__":
    main()
