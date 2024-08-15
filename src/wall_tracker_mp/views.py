from rest_framework.views import APIView
from django.http import JsonResponse
from django.http import Http404
from django.apps import apps
from django.core.cache import cache
from django.views import View
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

# from wall_tracker.models import WallProfile, MIN_WALL_HEIGHT, MAX_WALL_HEIGHT
from wall_tracker.stuff import make_response
from wall_tracker_mp.worker import Manager
from wall_tracker_mp.stuff import convert_mp_profiles, convert_mp_profiles_with_days

import logging
from uuid import uuid4
import asyncio
import time


_logger = logging.getLogger(__name__)


def get_profile(request, profile_id):
    try:
        profile = WallProfile.objects.get(id=profile_id)
        _logger.debug(f'Profile found: [{request.id=}; {profile=}]')
        return profile
    except WallProfile.DoesNotExist as e:
        _logger.debug(f'No profile found: [{request.id=}]', exc_info=e)
        raise Http404(make_response(request_id=request.id, 
                                    result='error', 
                                    desc='Not found', 
                                    status=HTTP_404_NOT_FOUND))


ICE_VOLUME_PER_DAY = 195
ICE_UNIT_COST = 1900
WALL_DAILY_GROW = 1 # ft


def check_value(val):
    if val <= 0:
        raise ValueError(f'Invalid value: [{val}]')


def get_total_daily_volume(day, heights):
    assert day > 0
    return sum(ICE_VOLUME_PER_DAY for h in heights if (MAX_WALL_HEIGHT - (h + day)) >= 0)


# class StartProcessView(APIView):
#     def post(self, request):
#         profiles = WallProfile.objects.all()
#         profiles = [p.initial_heights for p in profiles]
#         workers_num = 2

#         man = Manager(profiles, workers_num)
#         man.start()
#         StartProcessView.man = man


manager = None

def start_process():
    global manager
    if manager is None:
        from wall_tracker.models import WallProfile

        profiles = [list(p.initial_heights) for p in WallProfile.objects.all()]
        # workers_num = TeamsNumber.objects.all()[0].teams
        workers_num = 2
        # print(profiles)
        manager = Manager(profiles, workers_num)
        manager.start()

    while not manager.is_completed():
        time.sleep(0.1)
        
    manager.terminate()


class ProfileDailyIceVolumeView(View):
    async def get(self, request, profile_id, day):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, start_process)
        return make_response(request_id=request.id, data=dict(day=1, ice_amount=1))


class ProfileDailyCostView(APIView):
    def get(self, request, profile_id, day):
        try:
            profile = get_profile(request, profile_id)
        except Http404 as e:
            return e.args[0]

        cost = get_total_daily_volume(day, profile.initial_heights) * ICE_UNIT_COST
        return make_response(request_id=request.id, data=dict(day=day, cost=cost))


class AllProfilesDailyCostView(APIView):
    def get(self, request, day):
        try:
            profiles = WallProfile.objects.all()
        except Exception:
            _logger.debug(f'An unexpected error: [{request.id=}]', exc_info=e)
            return make_response(request_id=request.id, 
                                 result='error', 
                                 desc='Internal server error', 
                                 status=HTTP_500_INTERNAL_SERVER_ERROR)

        cost = 0
        for profile in profiles:
            cost += get_total_daily_volume(day, profile.initial_heights) * ICE_UNIT_COST
        return make_response(request_id=request.id, data=dict(day=day, cost=cost))


class TotalWallCostView(APIView):
    def get(self, request):
        try:
            profiles = WallProfile.objects.all()
        except Exception:
            _logger.debug(f'An unexpected error: [{request.id=}]', exc_info=e)
            return make_response(request_id=request.id, 
                                 result='error', 
                                 desc='Internal server error', 
                                 status=HTTP_500_INTERNAL_SERVER_ERROR)

        cost = 0
        for profile in profiles:
            for day in range(1, 31):
                cost += get_total_daily_volume(day, profile.initial_heights) * ICE_UNIT_COST

        return make_response(request_id=request.id, data=dict(day=None, cost=cost))


