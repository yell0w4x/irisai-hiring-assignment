from django.apps import AppConfig

from wall_tracker.stuff import setup_logger


class WallTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wall_tracker'

    def ready(self):
        setup_logger()
