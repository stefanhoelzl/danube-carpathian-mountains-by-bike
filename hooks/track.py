import re
import json
import threading
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler, test

from mkdocs.config import Config
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files


TrackPattern = r"track\((?P<url>[^)]+)\)"
TrackTemplate = f"""
<div class="track-map">
  <iframe src="https://gpx.studio/embed?options=TRACK_OPTIONS"></iframe>
</div>
"""

OPTIONS = {
    "token": "YOUR_MAPBOX_TOKEN",
    "basemap": "openTopoMap",
    "elevation": {
        "controls": False,
        "fill": "slope",
    }
}

class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

_RuntimeContext = {
    "base_url": "https://raw.githubusercontent.com/stefanhoelzl/danube-carpathian-mountains-by-bike/refs/heads/main/tracks/",
}

def on_startup(command: str, dirty: bool) -> None:
    if command != "gh-pages":
        _RuntimeContext["base_url"] = "http://localhost:8001/tracks/"

    if command == "serve":
        threading.Thread(
            target=test,
            args=[CORSRequestHandler, HTTPServer],
            kwargs={"port": 8001},
            daemon=True,
        ).start()

def on_page_markdown(markdown: str, page: Page, config: Config, files: Files) -> str:
    for match in re.finditer(TrackPattern, markdown):
        url = _RuntimeContext["base_url"] + match.group("url")
        markdown = markdown.replace(
            match.group(),
            TrackTemplate.replace(
                "TRACK_OPTIONS",
                urllib.parse.quote(
                    json.dumps(
                        {**OPTIONS, "files": [url]})
                )
            )
        )
    return markdown