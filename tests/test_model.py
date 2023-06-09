from datetime import date

from pytest import raises

from ironbot.models import Athlete, Event, Title


def test_title_equality():
    assert "PRO Event Calendar" == Title.CALENDAR
    assert "PRO EVENT CALENDAR" == Title.CALENDAR
    assert "Event Calendar" != Title.CALENDAR

    assert "Start Lists" == Title.START_LIST
    assert "start lists" == Title.START_LIST
    assert "Start List" != Title.START_LIST


def test_event_init():
    event = Event(
        name="Ironman Mont-Tremblant",
        when="08/20/2023",
        prize="50k",
        slots="2",
        registration="Open",
        deadline="TBD",
    )

    assert event.when == date(2023, 8, 20)
    assert str(event) == "2023-08-20\tIronman Mont-Tremblant\t50k\t2\tOpen\tTBD"


def test_event_with_missing_date():
    with raises(KeyError):
        Event(
            name="Ironman Mont-Tremblant",
            prize="50k",
            slots="2",
            registration="Open",
            deadline="TBD",
        )


def test_event_with_missing_date_value():
    with raises(TypeError):
        Event(
            when=None,
            name="Ironman Mont-Tremblant",
            prize="50k",
            slots="2",
            registration="Open",
            deadline="TBD",
        )


def test_event_with_invalid_date():
    with raises(ValueError):
        Event(
            name="Ironman Mont-Tremblant",
            when="20/08/2023",
            prize="50k",
            slots="2",
            registration="Open",
            deadline="TBD",
        )


def test_athlete_from_row():
    row = ("31", "WPRO", "BUCKINGHAM", "LUCY", "GBR", "F")
    athlete = Athlete.from_row("Ironman", row)
    assert athlete.bib == "31"
    assert athlete.category == "WPRO"
    assert athlete.name == "LUCY BUCKINGHAM"
    assert athlete.country == "GBR"
    assert str(athlete) == "31\tWPRO\tLUCY BUCKINGHAM\tGBR"


def test_athlete_without_bib():
    row = ("WPRO", "BUCKINGHAM", "LUCY", "GBR", "F")
    with raises(RuntimeError):
        Athlete.from_row("Ironman", row)


def test_athlete_without_last_name():
    row = ("31", "WPRO", "LUCY")
    with raises(RuntimeError):
        Athlete.from_row("Ironman", row)


def test_athlete_without_first_name():
    row = ("31", "WPRO", "BUCKINGHAM")
    with raises(RuntimeError):
        Athlete.from_row("Ironman", row)
