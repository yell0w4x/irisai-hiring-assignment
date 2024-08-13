from django.core.management.base import BaseCommand
from wall_tracker.models import WallProfile, WALL_MIN_HEIGHT, WALL_MAX_HEIGHT


class Command(BaseCommand):
    help = 'Add wall profile data to the database'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)

    def handle(self, *args, **options):
        input_file = options['input_file']

        profiles = dict()
        with open(input_file) as f:
            profiles = { 
                pid: [int(h) for h in line.strip().split()] for pid, line in enumerate(f, 1) 
            }

        for profile_id, heights in profiles.items():
            if any(h < WALL_MIN_HEIGHT or h > WALL_MAX_HEIGHT for h in heights):
                raise ValueError(f'Invalid height value given, profile id: [{profile_id}]')

            p = WallProfile(id=profile_id, initial_heights=heights)
            p.save()
