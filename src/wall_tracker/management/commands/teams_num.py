from django.core.management.base import BaseCommand
from wall_tracker.models import TeamsNumber


class Command(BaseCommand):
    help = 'Set number of workers to process. Please note existing data will be overwritten. (default: 1)'

    def add_arguments(self, parser):
        parser.add_argument('num', type=int)

    def handle(self, *args, **options):
        teams_num = options['num']
        TeamsNumber.objects.all().delete()
        TeamsNumber.objects.create(teams=teams_num)
