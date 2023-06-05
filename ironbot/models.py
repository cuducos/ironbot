from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from re import match
from typing import Iterator

from camelot import read_pdf  # type: ignore


CATEGORY = r"^[MWF](PRO)?$"


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
        self.date = datetime.strptime(self.when, "%m/%d/%Y").date()

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
            if field.isnumeric() and not fields["bib"]:
                fields["bib"] = field
            elif match(CATEGORY, field.upper()) and not fields["category"]:
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
