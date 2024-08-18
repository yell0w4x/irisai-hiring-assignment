import pytest
from unittest.mock import ANY

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


@pytest.mark.parametrize('path', ['/mp/profiles/1/days/1/', '/mp/profiles/1/overview/1/', '/mp/profiles/overview/1/', '/mp/profiles/overview/'])
def test_must_return_404_not_if_no_profiles_at_all(sut_base_url, path):
    response = requests.get(urljoin(sut_base_url, path))
    data = response.json()
    assert response.status_code == 404
    assert data['data'] == dict()
    assert data['meta']['result'] == 'error'
    assert data['meta']['desc'] == 'Not found'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None    


@pytest.mark.parametrize('path', ['/mp/profiles/1/days/1', '/asdf'])
def test_must_return_405_method_not_allowed_for_POST_request(sut_base_url, path):
    response = requests.post(urljoin(sut_base_url, path))
    data = response.json()
    assert response.status_code == 405
    assert data['data'] == dict()
    assert data['meta']['result'] == 'error'
    assert data['meta']['desc'] == 'Method not allowed'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.parametrize('profile_id, day', [(1, 1)])
def test_profile_daily_ice_amount(sut_base_url, profile_id, day):
    response = requests.get(urljoin(sut_base_url, f'/mp/profiles/{profile_id}/days/{day}'))
    assert response.status_code == 200
    data = response.json()
    assert data['data']['day'] == day
    assert data['data']['ice_amount'] == ANY
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.parametrize('profile_id, day', [(1, 1)])
def test_profile_daily_cost(sut_base_url, profile_id, day):
    response = requests.get(urljoin(sut_base_url, f'/mp/profiles/{profile_id}/overview/{day}'))
    assert response.status_code == 200
    data = response.json()
    assert data['data']['day'] == day
    assert data['data']['cost'] == ANY
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.parametrize('day', [i for i in range(1, 21)])
def test_all_profiles_daily_cost(sut_base_url, day):
    response = requests.get(urljoin(sut_base_url, f'/mp/profiles/overview/{day}'))
    assert response.status_code == 200
    data = response.json()
    assert data['data']['day'] == day
    assert data['data']['cost'] == ANY
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


def test_total_wall_cost(sut_base_url):
    response = requests.get(urljoin(sut_base_url, f'/mp/profiles/overview/'))
    assert response.status_code == 200
    data = response.json()
    assert data['data']['day'] == None
    assert data['data']['cost'] == ANY
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None
