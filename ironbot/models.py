from datetime import datetime
from enum import Enum
from re import match
from typing import Iterator

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import DeclarativeBase


CATEGORY = r"^[MWF](PRO)?$"


class Title(Enum):
    CALENDAR: str = "PRO Event Calendar"
    START_LIST: str = "Start Lists"

    def __eq__(self, other) -> bool:
        return self.value.lower() == other.strip().lower()


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    when = Column(Date)
    prize = Column(String)
    slots = Column(String)
    registration = Column(String)
    deadline = Column(String)

    def __init__(self, *args, **kwargs):
        kwargs["when"] = datetime.strptime(kwargs["when"], "%m/%d/%Y").date()
        return super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        fields = (
            self.when.strftime("%Y-%m-%d"),
            self.name,
            self.prize,
            self.slots,
            self.registration,
            self.deadline,
        )
        return "\t".join(str(field) for field in fields)

    def __repr__(self) -> str:
        return str(self)


class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(Integer, primary_key=True)
    event_name = Column(String, index=True)
    bib = Column(String, index=True)
    first_name = Column(String)
    last_name = Column(String)
    country = Column(String)
    category = Column(String)

    @classmethod
    def from_row(cls, event_name: str, row: Iterator[str]) -> "Athlete":
        fields = {col.name: "" for col in cls.__table__.columns if col.name != "id"}
        fields["event_name"] = event_name

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
        return "\t".join(str(field) for field in fields if field)

    def __repr__(self) -> str:
        return str(self)
