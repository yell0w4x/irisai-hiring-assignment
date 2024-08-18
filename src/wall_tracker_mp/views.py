from django.http import JsonResponse
from django.views import View
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from wall_tracker.stuff import make_response, make_404_not_found_response
from wall_tracker_mp.worker import Manager
from wall_tracker_mp.stuff import convert_mp_profiles, convert_mp_profiles_with_days

import logging
import asyncio
import time
from collections import Counter
import threading


_logger = logging.getLogger(__name__)


manager = None
profiles = None

ICE_VOLUME_PER_DAY = 195
ICE_UNIT_COST = 1900

lock = threading.Lock()
def start_process():
    global manager
    global profiles
    with lock:
        if manager is None:
            from wall_tracker.models import WallProfile, TeamsNumber

            profiles = [list(p.initial_heights) for p in WallProfile.objects.all()]
            teams = TeamsNumber.objects.all()
            workers_num = 1 if len(teams) == 0 else teams[0].teams
            manager = Manager(profiles, workers_num)
            oq = manager.output_queue()
            manager.start()
            profiles = oq.get()

        return profiles
        

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
    p = profiles
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

        try:
            original_profiles = await loop.run_in_executor(None, start_process)
            profiles_with_days = convert_mp_profiles_with_days(original_profiles)

            days = get_days_for_profile(profiles_with_days, profile_id, day)
            ice_amount = days * ICE_VOLUME_PER_DAY
            return make_response(request_id=request.id, data=dict(day=day, ice_amount=ice_amount))
        except (IndexError, ValueError):
            return make_404_not_found_response(request.id)


class ProfileDailyCostView(View):
    async def get(self, request, profile_id, day):
        loop = asyncio.get_running_loop()

        try:
            original_profiles = await loop.run_in_executor(None, start_process)
            profiles_with_days = convert_mp_profiles_with_days(original_profiles)

            days = get_days_for_profile(profiles_with_days, profile_id, day)
            cost = days * ICE_VOLUME_PER_DAY * ICE_UNIT_COST
            return make_response(request_id=request.id, data=dict(day=day, cost=cost))
        except (IndexError, ValueError):
            return make_404_not_found_response(request.id)


class AllProfilesDailyCostView(View):
    async def get(self, request, day):
        loop = asyncio.get_running_loop()

        try:
            original_profiles = await loop.run_in_executor(None, start_process)
            profiles_with_days = convert_mp_profiles_with_days(original_profiles)

            days = get_days_for_all_profiles(profiles_with_days, day)
            cost = days * ICE_VOLUME_PER_DAY * ICE_UNIT_COST
            return make_response(request_id=request.id, data=dict(day=day, cost=cost))
        except (IndexError, ValueError):
            return make_404_not_found_response(request.id)


class TotalWallCostView(View):
    async def get(self, request):
        loop = asyncio.get_running_loop()
        try:
            original_profiles = await loop.run_in_executor(None, start_process)
            profiles_with_days = convert_mp_profiles_with_days(original_profiles)
            days = sum(sum(len(sect) - 1 for sect in p) for p in profiles_with_days)
            cost = days * ICE_VOLUME_PER_DAY * ICE_UNIT_COST
            return make_response(request_id=request.id, data=dict(day=None, cost=cost))
        except ValueError:
            return make_404_not_found_response(request.id)

