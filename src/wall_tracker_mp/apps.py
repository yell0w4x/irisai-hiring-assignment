from django.apps import AppConfig

from thewall.settings import LOG_DIR
import shutil


class WallTrackerMpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wall_tracker_mp'

    def ready(self):
        shutil.rmtree(str(LOG_DIR), ignore_errors=True)
        LOG_DIR.mkdir(exist_ok=True)
