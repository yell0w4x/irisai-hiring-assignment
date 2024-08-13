from django.shortcuts import render
from rest_framework.views import APIView
from django.http import JsonResponse
from django.http import Http404
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from itertools import accumulate

from wall_tracker.models import WallProfile, MIN_WALL_HEIGHT, MAX_WALL_HEIGHT
from wall_tracker.stuff import make_response

import logging
from uuid import uuid4


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
    all_teams_vol = 0
    for h in heights:
        reminder = MAX_WALL_HEIGHT - (h + day)
        if reminder >= 0:
            all_teams_vol += ICE_VOLUME_PER_DAY

    return all_teams_vol


class ProfileDailyIceVolumeView(APIView):
    def get(self, request, profile_id, day):
        try:
            profile = get_profile(request, profile_id)
        except Http404 as e:
            return e.args[0]

        vol = get_total_daily_volume(day, profile.initial_heights)
        return make_response(request_id=request.id, data=dict(day=day, ice_amount=vol))


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
            return JsonResponse(data=dict(data=dict(), 
                                          meta=dict(id=request.id, result='error', desc='Internal server error')), 
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
            return JsonResponse(data=dict(data=dict(), 
                                          meta=dict(id=request.id, result='error', desc='Internal server error')), 
                                                    status=HTTP_500_INTERNAL_SERVER_ERROR)

        cost = 0
        for profile in profiles:
            for day in range(1, 31):
                cost += get_total_daily_volume(day, profile.initial_heights) * ICE_UNIT_COST

        return make_response(request_id=request.id, data=dict(day=None, cost=cost))


class UnmatchedView(APIView):
    def get(self, request):
        _logger.debug('Unmatched')
        return make_response(request_id=request.id, 
                             result='error', 
                             desc='Not found', 
                             status=HTTP_404_NOT_FOUND)
