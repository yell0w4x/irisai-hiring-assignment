"""
URL configuration for thewall project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler400, handler404, handler500

from wall_tracker.views import (ProfileDailyIceVolumeView, ProfileDailyCostView, 
                                AllProfilesDailyCostView, TotalWallCostView, 
                                NotFoundView, BadRequestView, InternalServerErrorView)

urlpatterns = [
    path('profiles/<int:profile_id>/days/<int:day>/', ProfileDailyIceVolumeView.as_view(), name='daily-ice-amount'),
    path('profiles/<int:profile_id>/overview/<int:day>/', ProfileDailyCostView.as_view(), name='daily-cost'),
    path('profiles/overview/<int:day>/', AllProfilesDailyCostView.as_view(), name='all-profiles-daily-cost'),
    path('profiles/overview/', TotalWallCostView.as_view(), name='total-wall-cost'),
    path('mp/', include('wall_tracker_mp.urls'))
]

handler400 = BadRequestView.as_view()
handler404 = NotFoundView.as_view()
handler500 = InternalServerErrorView.as_view()
