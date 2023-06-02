from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from importlib.metadata import version
from os import path
from tempfile import TemporaryDirectory
from re import match
from typing import Iterable, Iterator
from urllib.request import Request, urlopen, urlretrieve

from camelot import read_pdf  # type: ignore
from bs4 import BeautifulSoup


URL = "https://www.ironman.com/pro-athletes"
CALENDAR = "PRO Schedule".lower()
HEADERS = {"User-Agent": f"ironbot/{version('ironbot')}", "Accept": "*/*"}
CATEGORY = r"^[MF](PRO)?$"


def pdf_table_rows(url: str) -> Iterable[Iterator[str]]:
    with TemporaryDirectory() as tmp_dir:
        tmp = path.join(tmp_dir, "tmp.pdf")
        urlretrieve(url, tmp)

        tables = read_pdf(tmp, pages="all")
        if not tables:
            tables = read_pdf(tmp, pages="all", flavor="stream")

        for table in tables:
            yield from table.df.itertuples(index=False, name=None)


class Title(Enum):
    CALENDAR: str = "PRO Event Calendar"
    START_LIST: str = "Start Lists"

    def __eq__(self, other) -> bool:
        return self.value.lower() == other.strip().lower()


@dataclass
class Event:
    when: str
    name: str
    prize: str
    slots: str
    registration: str
    deadline: str

    def __post_init__(self) -> None:
        self.date = datetime.strptime(self.when, "%m/%d/%Y")

    def __str__(self) -> str:
        fields = (
            self.date.strftime("%Y-%m-%d"),
            self.name,
            self.prize,
            self.slots,
            self.registration,
            self.deadline,
        )
        return "\t".join(fields)


@dataclass
class Athlete:
    bib: str
    first_name: str
    last_name: str
    country: str
    category: str

    @classmethod
    def from_row(cls, row: Iterator[str]) -> "Athlete":
        fields = {key: "" for key in cls.__annotations__}

        for field in (field.strip() for field in row):
            if field.isnumeric():
                fields["bib"] = field
            elif match(CATEGORY, field.upper()):
                fields["category"] = field
            elif not fields["last_name"]:
                fields["last_name"] = field
            elif not fields["first_name"]:
                fields["first_name"] = field
            elif not fields["country"]:
                fields["country"] = field

        if not all(fields[key] for key in ("bib", "first_name", "last_name")):
            raise RuntimeError(f"Could not parse athlete from: {row}")

        return cls(**fields)

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        fields = (self.bib, self.category, self.name, self.country)
        return "\t".join(field for field in fields if field)


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
            try:
                yield Event(*row)
            except ValueError:
                pass

        return

    raise RuntimeError("Calendar URL not found")


def event_names(data: BeautifulSoup) -> Iterable[str]:
    yield from (a.text for a in data.find_all("a"))


def start_list(data: BeautifulSoup, event_number: int) -> Iterable[Athlete]:
    try:
        link = data.find_all("a")[event_number - 1]
    except IndexError:
        raise RuntimeError("Start list URL not found")

    for row in pdf_table_rows(link["href"]):
        try:
            yield Athlete.from_row(row)
        except RuntimeError:
            pass
