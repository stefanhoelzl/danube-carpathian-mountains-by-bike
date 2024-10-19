import re
import json
import urllib.parse
from pathlib import Path

from mkdocs.config import Config
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files, File, InclusionLevel

TrackPath = Path(__file__).parent.parent / "tracks"
TrackPattern = r"track\((?P<name>[^,]+),(?P<start>[^,]+),(?P<destination>[^,]+),(?P<distance>[^,]+),(?P<trip>[^,]+),(?P<total>[^,]+),(?P<ascent>[^,]+),(?P<descent>[^,]+)(,(?P<open>open))?\)"
TrackTemplate = """
<details {open}>
  <summary>{start} - {destination} {distance}km {trip}h / {total}h Ø{speed}km/h ↗{ascent}hm ↘{descent}hm</summary>
  <div class="track-map">
    <iframe src="https://gpx.studio/embed?options={options}" loading="lazy"></iframe>
  </div>
</details>
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
            TrackTemplate.format(
                start=_rfill(match.group("start"), 15, space="&nbsp;"),
                destination=_rfill(match.group("destination"), 18, space="&nbsp;"),
                distance=_lfill(match.group("distance"), 4, space="&nbsp;"),
                trip=_lfill(_minutes_to_hours(int(match.group("trip"))), 6, space="&nbsp;"),
                total=_lfill(_minutes_to_hours(int(match.group("total"))), 6, space="&nbsp;"),
                speed=_lfill(_speed(int(match.group("trip")), float(match.group("distance"))), 4, space="&npbsp;"),
                ascent=_lfill(match.group("ascent"), 5, space="&nbsp;"),
                descent=_lfill(match.group("descent"), 6, space="&nbsp;"),
                open=match.group("open"),
                options=urllib.parse.quote(
                    json.dumps(
                        {**OPTIONS, "files": [url]})
                )
            )
        )
    return markdown


def _rfill(value: str, size: int, *, space: str = " ") -> str:
    return f"{value}{space*max(0, size - len(value))}"


def _lfill(value: str, size: int, *, space: str = " ") -> str:
    return f"{space*max(0, size - len(value))}{value}"

def _minutes_to_hours(minutes: int) -> str:
    hours = minutes / 60
    full_hours = int(hours)
    minutes_rest = (minutes - (full_hours * 60))
    return f"{full_hours}:{minutes_rest:02}"

def _speed(minutes: int, km: float) -> str:
    return f"{km / (minutes / 60):.1f}"
