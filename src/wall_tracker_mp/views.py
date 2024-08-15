from django.http import JsonResponse
from django.views import View
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from wall_tracker.stuff import make_response
from wall_tracker_mp.worker import Manager
from wall_tracker_mp.stuff import convert_mp_profiles, convert_mp_profiles_with_days
from wall_tracker.views import ICE_UNIT_COST, ICE_VOLUME_PER_DAY

import logging
import asyncio
import time
from collections import Counter


_logger = logging.getLogger(__name__)


manager = None


def start_process():
    global manager
    if manager is None:
        from wall_tracker.models import WallProfile

        profiles = [list(p.initial_heights) for p in WallProfile.objects.all()]
        # workers_num = TeamsNumber.objects.all()[0].teams
        workers_num = 2
        manager = Manager(profiles, workers_num)
        manager.start()
        while not manager.is_completed():
            time.sleep(0.1)
        manager.terminate()

    while not manager.is_completed():
        time.sleep(0.1)

    return manager.profiles()
        

def get_days_for_profile(profiles, profile_id, day):
    c = Counter()
    p = profiles[profile_id - 1]
    for sect in p:
        d = dict(sect)
        if day in d:
            c[day] += 1

    if not c[day]:
        raise IndexError

    return c[day]


def get_days_for_all_profiles(profiles, day):
    c = Counter()
    p = profiles[profile_id - 1]
    for p in profiles:
        for sect in p:
            d = dict(sect)
            if day in d:
                c[day] += 1

    if not c[day]:
        raise IndexError

    return c[day]


class ProfileDailyIceVolumeView(View):
    async def get(self, request, profile_id, day):
        loop = asyncio.get_running_loop()
        original_profiles = await loop.run_in_executor(None, start_process)
        profiles_with_days = convert_mp_profiles_with_days(original_profiles)
        # profiles = convert_mp_profiles(original_profiles)

        # print(profiles_with_days)
        # print(profiles)

        try:
            days = get_days_for_profile(profiles_with_days, profile_id, day)
            ice_amount = days * ICE_VOLUME_PER_DAY
            return make_response(request_id=request.id, data=dict(day=day, ice_amount=ice_amount))
        except IndexError:
            return make_response(request_id=request.id, 
                                 result='error', 
                                 desc='Not found', 
                                 status=HTTP_404_NOT_FOUND)


class ProfileDailyCostView(View):
    async def get(self, request, profile_id, day):
        loop = asyncio.get_running_loop()
        original_profiles = await loop.run_in_executor(None, start_process)
        profiles_with_days = convert_mp_profiles_with_days(original_profiles)

        try:
            days = get_days_for_profile(profiles_with_days, profile_id, day)
            cost = days * ICE_VOLUME_PER_DAY * ICE_UNIT_COST
            return make_response(request_id=request.id, data=dict(day=day, cost=cost))
        except IndexError:
            return make_response(request_id=request.id, 
                                 result='error', 
                                 desc='Not found', 
                                 status=HTTP_404_NOT_FOUND)


class AllProfilesDailyCostView(View):
    async def get(self, request, day):
        loop = asyncio.get_running_loop()
        original_profiles = await loop.run_in_executor(None, start_process)
        profiles_with_days = convert_mp_profiles_with_days(original_profiles)

        try:
            days = get_days_for_all_profiles(profiles_with_days, day)
            cost = days * ICE_VOLUME_PER_DAY * ICE_UNIT_COST
            return make_response(request_id=request.id, data=dict(day=day, cost=cost))
        except IndexError:
            return make_response(request_id=request.id, 
                                 result='error', 
                                 desc='Not found', 
                                 status=HTTP_404_NOT_FOUND)


class TotalWallCostView(View):
    async def get(self, request):
        loop = asyncio.get_running_loop()
        original_profiles = await loop.run_in_executor(None, start_process)
        profiles_with_days = convert_mp_profiles_with_days(original_profiles)
        days = sum(sum(len(sect) - 1 for sect in p) for p in profiles_with_days)
        cost = days * ICE_VOLUME_PER_DAY * ICE_UNIT_COST
        return make_response(request_id=request.id, data=dict(day=None, cost=cost))
