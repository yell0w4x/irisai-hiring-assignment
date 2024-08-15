from django.core.management.base import BaseCommand
# from wall_tracker_mp.models import TeamsNumber


class Command(BaseCommand):
    help = 'Add wall profile data to the database. Please note existing data will be overwritten.'

    def add_arguments(self, parser):
        parser.add_argument('num', type=int)

    def handle(self, *args, **options):
        teams_num = options['num']
        # TeamsNumber.objects.all().delete()
        # TeamsNumber.objects.create(teams=teams_num)
