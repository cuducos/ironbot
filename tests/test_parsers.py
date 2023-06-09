from datetime import date

from ironbot.models import Event
from ironbot.parsers import EventParser


def test_simple_event():
    row = ("8/20/2023", "Ironman", "0", "1", "Open", "TBD")
    parser = EventParser(row)
    events = tuple(parser)

    assert len(events) == 1
    assert events[0].when == date(2023, 8, 20)
    assert events[0].name == "Ironman"
    assert events[0].prize == "0"
    assert events[0].slots == "1"
    assert events[0].registration == "Open"
    assert events[0].deadline == "TBD"


def test_multi_event():
    row = ("8/20/2023 (AG)\n8/21/2023 (Ceremony)", "Ironman", "0", "1", "Open", "TBD")
    parser = EventParser(row)
    events = tuple(parser)

    assert len(events) == 2
    assert events[0].name == "Ironman (AG)"
    assert events[1].name == "Ironman (Ceremony)"
    assert events[0].when == date(2023, 8, 20)
    assert events[1].when == date(2023, 8, 21)
    assert events[0].prize == events[1].prize
    assert events[0].slots == events[1].slots
    assert events[0].registration == events[1].registration
    assert events[0].deadline == events[1].deadline


def test_header_for_event_table():
    row = ("Date", "Event", "Prize", "Slots", "Registration", "Deadline")
    parser = EventParser(row)
    events = tuple(parser)

    assert len(events) == 0
