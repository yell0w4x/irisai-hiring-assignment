from django.urls import path

from wall_tracker_mp.views import (ProfileDailyIceVolumeView, ProfileDailyCostView, 
                                  AllProfilesDailyCostView, TotalWallCostView)

urlpatterns = [
    path('profiles/<int:profile_id>/days/<int:day>/', ProfileDailyIceVolumeView.as_view(), name='mp-daily-ice-amount'),
    path('profiles/<int:profile_id>/overview/<int:day>/', ProfileDailyCostView.as_view(), name='mp-daily-cost'),
    path('profiles/overview/<int:day>/', AllProfilesDailyCostView.as_view(), name='mp-all-profiles-daily-cost'),
    path('profiles/overview/', TotalWallCostView.as_view(), name='mp-total-wall-cost'),
]
