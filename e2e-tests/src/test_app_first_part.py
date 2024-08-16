import pytest

import logging
import re
import requests
from urllib.parse import urljoin
import time
import subprocess


ICE_VOLUME_PER_DAY = 195
ICE_UNIT_COST = 1900


_logger = logging.getLogger(__name__)


APP_ENDPOINT = 'e2e-app-instance:8000'
@pytest.fixture
def app_endpoint():
    return APP_ENDPOINT


@pytest.fixture(autouse=True)
def wait_for_sut(app_endpoint):
    subprocess.check_call(['/test/wait-for-it.sh', app_endpoint, '-t', '30'])


@pytest.fixture
def sut_base_url(app_endpoint):
    return f'http://{app_endpoint}'


UUID_REGEX = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'


# NOTE: Looks like it's django bug. Same integration test with made using django test client passes.
# NOTE: But real app behaves differently. Though it responds with 404, but this 404 yielded from django level.
# NOTE: And the response has html body. These requests don't reach app at all.
# NOTE: See same named test in views_test.py

@pytest.mark.parametrize('path', ['/profiles', 
                                 '/profiles/',
                                 '/profiles/1/days/-1', 
                                 'profiles/10/days/1/',
                                 '/profiles/-1/days/1',
                                 '/asdf',
                                 ])
def test_must_return_404_not_found_for_any_unknown_url(sut_base_url, path):
    response = requests.get(urljoin(sut_base_url, path))
    assert response.status_code == 404

    if path != 'profiles/10/days/1/':
        # XFAIL
        pytest.xfail('Seems django bug, these methods even don\'t reach app 404 handler, '
            'thouth they shuold. The same test with django test client passes.')

    data = response.json()
    assert data['data'] == dict()
    assert data['meta']['result'] == 'error'
    assert data['meta']['desc'] == 'Not found'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.parametrize('path', ['/profiles/1/days/1', '/asdf'])
@pytest.mark.parametrize('method', ['POST', 'PUT', 'DELETE', 'PATCH', 'CONNECT'])
def test_must_return_405_method_not_allowed_for_POST_request(sut_base_url, path, method):
    response = requests.request(method, urljoin(sut_base_url, path))
    data = response.json()
    assert response.status_code == 405
    assert data['data'] == dict()
    assert data['meta']['result'] == 'error'
    assert data['meta']['desc'] == 'Method not allowed'
    assert re.match(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', data['meta']['id']) is not None


DAILY_ICE_VOL = ICE_VOLUME_PER_DAY
@pytest.mark.parametrize('profile_id, day, ice_amount', [(1, 1, DAILY_ICE_VOL*3), (1, 2, DAILY_ICE_VOL*3), (1, 3, DAILY_ICE_VOL*2), 
                                                         (1, 4, DAILY_ICE_VOL*2), (1, 5, DAILY_ICE_VOL*2), (1, 6, DAILY_ICE_VOL),
                                                         (1, 7, DAILY_ICE_VOL), (1, 8, DAILY_ICE_VOL), (1, 9, DAILY_ICE_VOL),
                                                         (1, 10, 0),
                                                         # 2nd profile
                                                         *[(2, day, DAILY_ICE_VOL) for day in range(1, 14)],
                                                         # an extra day where work is done
                                                         (2, 14, 0),
                                                         # 3rd profile
                                                         *[(3, day, DAILY_ICE_VOL*5) for day in range(1, 9)],
                                                         *[(3, day, DAILY_ICE_VOL*4) for day in range(9, 12)],
                                                         *[(3, day, DAILY_ICE_VOL*3) for day in range(12, 14)],
                                                         # add some extra days where work is already completed
                                                         *[(3, day, DAILY_ICE_VOL*0) for day in range(14, 17)], 
                                                         ])
def test_profile_daily_ice_amount(sut_base_url, profile_id, day, ice_amount):
    response = requests.get(urljoin(sut_base_url, f'/profiles/{profile_id}/days/{day}/'))
    assert response.status_code == 200
    data = response.json()
    assert data['data']['day'] == day
    assert data['data']['ice_amount'] == ice_amount
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


DAILY_COST = DAILY_ICE_VOL * ICE_UNIT_COST
@pytest.mark.parametrize('profile_id, day, cost', [(1, 1, DAILY_COST*3), (1, 2, DAILY_COST*3), (1, 3, DAILY_COST*2), 
                                                   (1, 4, DAILY_COST*2), (1, 5, DAILY_COST*2), (1, 6, DAILY_COST),
                                                   (1, 7, DAILY_COST), (1, 8, DAILY_COST), (1, 9, DAILY_COST),
                                                   (1, 10, 0),
                                                   # 2nd profile
                                                   *[(2, day, DAILY_COST) for day in range(1, 14)],
                                                   # an extra day where work is done
                                                   (2, 14, 0),
                                                   # 3rd profile
                                                   *[(3, day, DAILY_COST*5) for day in range(1, 9)],
                                                   *[(3, day, DAILY_COST*4) for day in range(9, 12)],
                                                   *[(3, day, DAILY_COST*3) for day in range(12, 14)],
                                                   # add some extra days where work is already completed
                                                   *[(3, day, DAILY_COST*0) for day in range(14, 17)], 
                                                   ])
def test_profile_daily_cost(sut_base_url, profile_id, day, cost):
    response = requests.get(urljoin(sut_base_url, f'/profiles/{profile_id}/overview/{day}/'))
    assert response.status_code == 200
    data = response.json()
    assert data['data']['day'] == day
    assert data['data']['cost'] == cost
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.parametrize('day, cost', [(1, DAILY_COST*3 + DAILY_COST + DAILY_COST*5), 
                                       (2, DAILY_COST*3 + DAILY_COST + DAILY_COST*5),
                                       (3, DAILY_COST*2 + DAILY_COST + DAILY_COST*5), 
                                       (6, DAILY_COST + DAILY_COST + DAILY_COST*5),
                                       (8, DAILY_COST + DAILY_COST + DAILY_COST*5),
                                       (9, DAILY_COST + DAILY_COST + DAILY_COST*4),
                                       (10, 0 + DAILY_COST + DAILY_COST*4),
                                       (11, 0 + DAILY_COST + DAILY_COST*4),
                                       (12, 0 + DAILY_COST + DAILY_COST*3),
                                       (13, 0 + DAILY_COST + DAILY_COST*3),
                                       (14, 0 + 0 + 0),
                                        ])
def test_all_profiles_daily_cost(sut_base_url, day, cost):
    response = requests.get(urljoin(sut_base_url, f'/profiles/overview/{day}/'))
    assert response.status_code == 200
    data = response.json()
    assert data['data']['day'] == day
    assert data['data']['cost'] == cost
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


def test_total_wall_cost(sut_base_url):
    response = requests.get(urljoin(sut_base_url, f'/profiles/overview/'))
    assert response.status_code == 200
    data = response.json()
    assert data['data']['day'] == None
    assert data['data']['cost'] == 32_233_500
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.parametrize('path', ['/profiles/1/days/1/', '/profiles/1/overview/1/', '/profiles/overview/1/', '/profiles/overview/'])
def test_must_return_404_not_if_no_profiles_at_all(sut_base_url, path):
    response = requests.get(urljoin(sut_base_url, path))
    data = response.json()
    assert response.status_code == 404
    assert data['data'] == dict()
    assert data['meta']['result'] == 'error'
    assert data['meta']['desc'] == 'Not found'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None    