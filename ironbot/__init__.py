from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, Iterator
from urllib.request import urlretrieve

from bs4 import BeautifulSoup
from httpx import get
from pdftotext import PDF  # type: ignore


URL = "https://www.ironman.com/pro-athletes"
CALENDAR = "PRO Schedule".lower()


class Title(Enum):
    CALENDAR: str = "PRO Event Calendar"
    START_LIST: str = "Start Lists"

    def __eq__(self, other) -> bool:
        return self.value.lower() == other.strip().lower()


@dataclass
class Event:
    when: date
    name: str
    prize: str
    slots: str
    registration: str
    deadline: str

    def __str__(self) -> str:
        fields = (
            self.when.strftime("%Y-%m-%d"),
            self.name,
            self.prize,
            self.slots,
            self.registration,
            self.deadline,
        )
        return "\t".join(fields)


class EventParser:
    def __init__(self, text):
        self.lines = tuple(line for line in text.split("\n") if line.strip())

    @staticmethod
    def to_date(line: str) -> date:
        return datetime.strptime(line, "%m/%d/%Y").date()

    def __iter__(self) -> Iterator[Event]:
        next_idx = 0
        for idx, line in enumerate(self.lines):
            if idx < next_idx:
                continue

            if not line.strip():
                continue

            try:
                when = self.to_date(line)
            except ValueError:
                continue

            next_idx = idx + 5
            yield Event(when, *self.lines[idx + 1 : next_idx + 1])


def load(title: Title) -> BeautifulSoup:
    resp = get(URL)
    dom = BeautifulSoup(resp.content, features="html.parser")
    for h3 in dom.find_all("h3"):
        if h3.text != title:
            continue

        return h3.parent

    raise RuntimeError(f"HTML block not found for {title}")


def events(data: BeautifulSoup) -> Iterable[Event]:
    url = None
    for a in data.find_all("a"):
        if a.text.strip().lower() != CALENDAR:
            continue

        url = a["href"]
        break

    if not url:
        raise RuntimeError("Calendar URL not found")

    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir) / "tmp.pdf"
        urlretrieve(url, tmp)
        with tmp.open("rb") as file_handler:
            pdf = PDF(file_handler)
            text = "\n".join(pdf)
            return EventParser(text)


def event_names(data: BeautifulSoup) -> Iterable[str]:
    yield from (a.text for a in data.find_all("a"))


def start_list(data: BeautifulSoup, event_number: int) -> str:
    for number, a in enumerate(data.find_all("a"), 1):
        if number != event_number:
            continue

        return a["href"]

    raise RuntimeError("Start list URL not found")
