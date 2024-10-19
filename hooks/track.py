import re
import json
import urllib.parse
from pathlib import Path

from mkdocs.config import Config
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files, File, InclusionLevel

TrackPath = Path(__file__).parent.parent / "tracks"
TrackPattern = r"track\((?P<name>[^)]+)\)"
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

def on_files(files: Files, config: Config) -> Files:
    for track in TrackPath.glob("*.gpx"):
        files.append(
            File(
                track.name,
                str(track.parent),
                str(Path(config["site_dir"], "tracks")),
                use_directory_urls=False,
                inclusion=InclusionLevel.NOT_IN_NAV
            )
        )
    return files

def on_page_markdown(markdown: str, page: Page, config: Config, files: Files) -> str:
    for match in re.finditer(TrackPattern, markdown):
        url = urllib.parse.urljoin(config["site_url"], f"tracks/{match.group('name')}")
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