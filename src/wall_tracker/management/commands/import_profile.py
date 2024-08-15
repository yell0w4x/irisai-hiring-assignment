from django.core.management.base import BaseCommand
from wall_tracker.models import WallProfile, MIN_WALL_HEIGHT, MAX_WALL_HEIGHT


class Command(BaseCommand):
    help = 'Add wall profile data to the database. Please note existing data will be overwritten.'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)

    def handle(self, *args, **options):
        input_file = options['input_file']

        profiles = dict()
        with open(input_file) as f:
            profiles = [[int(h) for h in line.strip().split()] for line in f if line.strip()]

        WallProfile.objects.all().delete()
        for profile_id, heights in enumerate(profiles, 1):
            if any(h < MIN_WALL_HEIGHT or h > MAX_WALL_HEIGHT for h in heights):
                raise ValueError(f'Invalid height value given, profile id: [{profile_id}]')

            p = WallProfile.objects.create(id=profile_id, initial_heights=heights)
