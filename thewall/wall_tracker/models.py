from django.db import models


WALL_MIN_HEIGHT=0
WALL_MAX_HEIGHT=30


class WallProfile(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    initial_heights = models.JSONField()