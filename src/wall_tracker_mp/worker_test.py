import pytest
import os
import shutil
import copy
import random
import time

from thewall.settings import LOG_DIR
from wall_tracker.stuff import setup_logger
from wall_tracker_mp.worker import Manager
from wall_tracker.models import MAX_WALL_HEIGHT
from wall_tracker_mp.stuff import convert_mp_profiles


@pytest.fixture
def log_setup():
    shutil.rmtree(str(LOG_DIR), ignore_errors=True)
    LOG_DIR.mkdir(exist_ok=True)
    os.environ['LOG_NO_COLOR'] = '1'
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['DEPS_LOG_LEVEL'] = 'INFO'
    setup_logger()


# @pytest.fixture
# def profiles():
#     return [
#         [21, 25, 28],
#         [17],
#         [17, 22, 17, 19, 17]
#     ]


@pytest.fixture
def profiles():
    WALLS_COUNT = 2
    MAX_SECTIONS_COUNT = 2000
    return [[random.randint(0, MAX_WALL_HEIGHT) for _ in range(random.randint(MAX_SECTIONS_COUNT // 3, MAX_SECTIONS_COUNT))] for _ in range(WALLS_COUNT)]


def profiles_to_expected(profiles):
    profiles = copy.deepcopy(profiles)
    for p in profiles:
        for i, sect in enumerate(p):
            p[i] = [j for j in range(sect, MAX_WALL_HEIGHT + 1)]

    return profiles


ITERATIONS = 1
@pytest.mark.parametrize('workers_num', [10, 25, 50])
@pytest.mark.parametrize('iter', [i for i in range(ITERATIONS)])
def test_workers(log_setup, profiles, workers_num, iter):
    print(f'ITERATION: {iter}, TOTAL SECTIONS: {sum(len(p) for p in profiles)}, WORKERS: {workers_num}')
    time.sleep(0.5)

    man = Manager(profiles, workers_num)
    oq = man.output_queue()
    man.start()
    mp_profiles = oq.get()
    expected = profiles_to_expected(profiles)
    result = convert_mp_profiles(mp_profiles)
    assert expected == result


def test_workers_must_reject_empty_profile():
    with pytest.raises(ValueError):
        man = Manager([], 1)
