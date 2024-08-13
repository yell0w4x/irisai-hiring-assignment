from django.db import models


MIN_WALL_HEIGHT=0
MAX_WALL_HEIGHT=30


class WallProfile(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    initial_heights = models.JSONField()