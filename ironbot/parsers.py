from typing import Generator, Iterable, Optional

from ironbot.models import Event


class EventParser:
    COLUMNS = ("when", "name", "prize", "slots", "registration", "deadline")

    def __init__(self, row: Iterable[str]):
        self.original_row = row

    def parse(self, row: Iterable[str]) -> Optional[Event]:
        kwargs = dict(zip(self.COLUMNS, row))
        try:
            return Event(**kwargs)
        except (TypeError, KeyError, ValueError):
            return None

    def _events(self) -> Iterable[Optional[Event]]:
        when, *_ = self.original_row
        if "\n" not in when:
            yield self.parse(self.original_row)
            return

        for details in when.split("\n"):
            new_row = list(self.original_row)
            when, category = details.split(" ", 1)
            new_row[0] = when.strip()
            new_row[1] = f"{new_row[1]} {category.strip()}"
            yield self.parse(new_row)

    def __iter__(self) -> Generator[Event, None, None]:
        yield from (event for event in self._events() if event)
