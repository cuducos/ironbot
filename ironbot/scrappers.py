from importlib.metadata import version
from os import path
from tempfile import TemporaryDirectory
from typing import Iterable, Iterator, Union
from urllib.request import Request, urlopen, urlretrieve

from bs4 import BeautifulSoup
from camelot import read_pdf  # type: ignore

from ironbot.models import Athlete, Event, Title
from ironbot.parsers import EventParser

URL = "https://www.ironman.com/pro-athletes"
CALENDAR = "PRO Schedule".lower()
HEADERS = {"User-Agent": f"ironbot/{version('ironbot')}", "Accept": "*/*"}


def pdf_table_rows(url: str) -> Iterable[Iterator[str]]:
    with TemporaryDirectory() as tmp_dir:
        tmp = path.join(tmp_dir, "tmp.pdf")
        urlretrieve(url, tmp)

        tables = read_pdf(tmp, pages="all")
        if not tables:
            tables = read_pdf(tmp, pages="all", flavor="stream")

        for table in tables:
            yield from table.df.itertuples(index=False, name=None)


def load(title: Title) -> BeautifulSoup:
    req = Request(URL, headers=HEADERS)
    with urlopen(req) as resp:
        dom = BeautifulSoup(resp, features="html.parser")
        for h3 in dom.find_all("h3"):
            if h3.text != title:
                continue

            return h3.parent

    raise RuntimeError(f"HTML block not found for {title}")


def events(data: BeautifulSoup) -> Iterable[Event]:
    for a in data.find_all("a"):
        if a.text.strip().lower() != CALENDAR:
            continue

        for row in pdf_table_rows(a["href"]):
            yield from EventParser(row)

        return

    raise RuntimeError("Calendar URL not found")


def event_names(data: BeautifulSoup) -> Iterable[str]:
    yield from (a.text for a in data.find_all("a"))


def start_list(data: Union[BeautifulSoup, str], event_name: str) -> Iterable[Athlete]:
    if isinstance(data, str):
        data = BeautifulSoup(data, features="html.parser")

    links = (link for link in data.find_all("a") if link.text == event_name)
    try:
        link = next(links)
    except StopIteration:
        raise RuntimeError("Start list URL not found")

    for row in pdf_table_rows(link["href"]):
        try:
            yield Athlete.from_row(event_name, row)
        except RuntimeError:
            pass
