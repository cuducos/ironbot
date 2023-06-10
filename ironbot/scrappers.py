from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, Iterator

from camelot import read_pdf  # type: ignore
from bs4 import BeautifulSoup
from httpx import AsyncClient

from ironbot.models import Athlete, Event, Title
from ironbot.parsers import EventParser


URL = "https://www.ironman.com/pro-athletes"
CALENDAR = "PRO Schedule".lower()
HEADERS = {"User-Agent": f"ironbot/{version('ironbot')}", "Accept": "*/*"}


async def pdf_table_rows(client: AsyncClient, url: str) -> Iterable[Iterator[str]]:
    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir) / "tmp.pdf"
        resp = await client.get(url)
        tmp.write_bytes(await resp.aread())

        tables = read_pdf(str(tmp), pages="all")
        if not tables:
            tables = read_pdf(str(tmp), pages="all", flavor="stream")

        return tuple(
            row
            for table in tables
            for row in table.df.itertuples(index=False, name=None)
        )


async def load(client: AsyncClient, title: Title) -> BeautifulSoup:
    resp = await client.get(URL, headers=HEADERS)
    dom = BeautifulSoup(await resp.aread(), features="html.parser")
    for h3 in dom.find_all("h3"):
        if h3.text != title:
            continue

        return h3.parent

    raise RuntimeError(f"HTML block not found for {title}")


async def events(client: AsyncClient, data: BeautifulSoup) -> Iterable[Event]:
    for a in data.find_all("a"):
        if a.text.strip().lower() != CALENDAR:
            continue

        rows = await pdf_table_rows(client, a["href"])
        parsers = (EventParser(row) for row in rows)
        return tuple(event for parser in parsers for event in parser)

    raise RuntimeError("Calendar URL not found")


def event_names(data: BeautifulSoup) -> Iterable[str]:
    yield from (a.text for a in data.find_all("a"))


async def start_list(
    client: AsyncClient, data: BeautifulSoup, event_name: str
) -> Iterable[Athlete]:
    links = (link for link in data.find_all("a") if link.text == event_name)
    try:
        link = next(links)
    except StopIteration:
        raise RuntimeError("Start list URL not found")

    rows = await pdf_table_rows(client, link["href"])
    athletes = []
    for row in rows:
        try:
            athletes.append(Athlete.from_row(event_name, row))
        except RuntimeError:
            pass
    return athletes
