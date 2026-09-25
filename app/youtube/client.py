from ytmusicapi import YTMusic


def _text(value):
    if isinstance(value, dict): return value.get("text", "")
    return str(value or "")


def normalize(item):
    artists = item.get("artists") or []
    album = item.get("album") or {}
    thumbs = item.get("thumbnails") or []
    return {"video_id": item.get("videoId", ""), "title": item.get("title", "Untitled"),
            "artist": ", ".join(_text(a) for a in artists) or "Unknown artist",
            "album": _text(album.get("name", "")) if isinstance(album, dict) else _text(album),
            "thumbnail": thumbs[-1].get("url", "") if thumbs else "", "duration": item.get("duration", "")}


class YouTubeMusic:
    def __init__(self): self.client = YTMusic()
    def search(self, query):
        return [normalize(x) for x in self.client.search(query, filter="songs") if x.get("videoId")]
    def suggestions(self, query): return self.client.get_search_suggestions(query)
