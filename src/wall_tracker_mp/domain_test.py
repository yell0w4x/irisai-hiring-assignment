import pytest

from wall_tracker_mp.domain import WallSection, WallProfile
from wall_tracker.models import MAX_WALL_HEIGHT


def test_section():
    with pytest.raises(AssertionError):
        WallSection(MAX_WALL_HEIGHT + 1, 0, 0)

    sut = WallSection(MAX_WALL_HEIGHT - 2, 1, 2)
    assert sut.section_id() == 1
    assert sut.profile_id() == 2
    sut.steps_num() == 2
    assert not sut.is_completed()

    sut.build_step(1)
    assert not sut.is_completed()

    sut.build_step(3)
    assert sut.is_completed()

    assert not sut.is_busy()
    sut.set_busy()
    assert sut.is_busy()
    assert sut.days() == [0, 1, 3]


def test_profile():
    sut = WallProfile([27, 28, 29, 30], profile_id=1)
    assert not sut.is_completed()
    sect = sut.get_uncompleted_section()
    assert not sect.is_completed()

    assert list(sect.steps()) == [27, 0, 0, 0]
    sect.steps_num() == 3

    sect.build_step(1)
    assert list(sect.steps()) == [27, 28, 0, 0]

    sect.build_step(2)
    assert list(sect.steps()) == [27, 28, 29, 0]

    sect.build_step(3)
    assert list(sect.steps()) == [27, 28, 29, 30]

    sect.build_step(4)
    assert list(sect.steps()) == [27, 28, 29, 30]

    assert not sut.is_completed()
    sect = sut.get_uncompleted_section()

    assert list(sect.steps()) == [28, 0, 0]
    sect.build_step(5)
    sect.build_step(6)
    assert list(sect.steps()) == [28, 29, 30]

    assert not sut.is_completed()
    sect = sut.get_uncompleted_section()
    assert list(sect.steps()) == [29, 0]
    sect.build_step(7)
    assert list(sect.steps()) == [29, 30]

    assert sut.is_completed()
    assert sut.get_uncompleted_section() is None

    sect = sut.get_available_section()
    sect.set_busy()
    sect = sut.get_available_section()
    sect.set_busy()
    sect = sut.get_available_section()
    sect.set_busy()
    sect = sut.get_available_section()
    sect.set_busy()
    assert sut.get_available_section() is None


