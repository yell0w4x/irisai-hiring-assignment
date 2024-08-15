from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db import connection

from thewall.settings import LOG_DIR
import shutil


class WallTrackerMpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wall_tracker_mp'

    def ready(self):
        shutil.rmtree(str(LOG_DIR), ignore_errors=True)
        LOG_DIR.mkdir(exist_ok=True)
        # post_migrate.connect(self.dummy, sender=self)

    # def dummy(self, *args, **kwargs):
    #     if connection.connection is not None:
    #         subprocess.Popen(['bash', '-c', 'sleep 2 && wget -qO- http://127.0.0.1:8000/mp/profiles/1/overview/1/'])
    #         print('asdf')
