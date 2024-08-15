import pytest

from django.urls import reverse
from wall_tracker.models import WallProfile
from wall_tracker.stuff import setup_logger
import logging
import json
import re

from wall_tracker.views import ICE_VOLUME_PER_DAY, ICE_UNIT_COST


_logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def logger_setup():
    setup_logger()


@pytest.fixture
def clear_db():
    WallProfile.objects.all().delete()


@pytest.fixture
def profiles(clear_db):
    profile1 = WallProfile.objects.create(id=1, initial_heights=[21, 25, 28])
    profile2 = WallProfile.objects.create(id=2, initial_heights=[17])
    profile3 = WallProfile.objects.create(id=3, initial_heights=[17, 22, 17, 19, 17])
    return profile1, profile2, profile3


UUID_REGEX = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'


@pytest.mark.parametrize('url', ['/profiles', 
                                 '/profiles/',
                                 '/profiles/1/days/-1', 
                                 'profiles/5/days/1/',
                                 '/profiles/-1/days/1',
                                 '/asdf',
                                 ])
@pytest.mark.django_db(databases=['TEST', 'default'])
def test_must_return_404_not_found_for_any_unknown_url(client, profiles, url):
    response = client.get(url)

    assert response.status_code == 404

    data = response.json()
    assert data['data'] == dict()
    assert data['meta']['result'] == 'error'
    assert data['meta']['desc'] == 'Not found'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.parametrize('url', ['/profiles/1/days/1', '/asdf'])
def test_must_return_405_method_not_allowed_for_POST_request(client, url):
    response = client.post(url)
    assert response.status_code == 405

    data = response.json()
    assert data['data'] == dict()
    assert data['meta']['result'] == 'error'
    assert data['meta']['desc'] == 'Method not allowed'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


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
@pytest.mark.django_db(databases=['TEST', 'default'])
def test_profile_daily_ice_amount(client, profiles, profile_id, day, ice_amount):
    _logger.debug(list(item.initial_heights for item in WallProfile.objects.all()))

    assert WallProfile.objects.count() == 3
    url = reverse('daily-ice-amount', kwargs=dict(profile_id=profile_id, day=day))
    response = client.get(url)
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
@pytest.mark.django_db(databases=['TEST', 'default'])
def test_profile_daily_cost(client, profiles, profile_id, day, cost):
    url = reverse('daily-cost', kwargs=dict(profile_id=profile_id, day=day))
    response = client.get(url)
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
@pytest.mark.django_db(databases=['TEST', 'default'])
def test_all_profiles_daily_cost(client, profiles, day, cost):
    url = reverse('all-profiles-daily-cost', kwargs=dict(day=day))
    response = client.get(url)
    assert response.status_code == 200

    data = response.json()
    assert data['data']['day'] == day
    assert data['data']['cost'] == cost
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.django_db(databases=['TEST', 'default'])
def test_total_wall_cost(client, profiles):
    url = reverse('total-wall-cost')
    response = client.get(url)
    assert response.status_code == 200

    data = response.json()
    assert data['data']['day'] == None
    assert data['data']['cost'] == 32_233_500
    assert data['meta']['result'] == 'success'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None


@pytest.mark.django_db(databases=['TEST', 'default'])
@pytest.mark.parametrize('path', ['/profiles/1/days/1/', '/profiles/1/overview/1/', '/profiles/overview/1/', '/profiles/overview/'])
def test_must_return_404_not_if_no_profiles_at_all(clear_db, client, path):
    response = client.get(path)
    data = response.json()
    assert response.status_code == 404
    assert data['data'] == dict()
    assert data['meta']['result'] == 'error'
    assert data['meta']['desc'] == 'Not found'
    assert re.match(UUID_REGEX, data['meta']['id']) is not None    