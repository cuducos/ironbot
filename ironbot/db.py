from contextlib import contextmanager
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Iterable

from ironbot.models import Athlete, Event


@dataclass
class Database:
    url: str

    @contextmanager
    def session(self):
        with Session(create_engine(self.url)) as session:
            yield session

    def save_events(self, events: Iterable[Event]) -> int:
        with self.session() as session:
            for count, event in enumerate(events):
                session.add(event)
            session.commit()
            return count

    def save_athletes(self, athletes: Iterable[Athlete]) -> int:
        with self.session() as session:
            for count, athlete in enumerate(athletes):
                session.add(athlete)
            session.commit()
            return count
