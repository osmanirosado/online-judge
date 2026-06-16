from django.core.management import BaseCommand

from judge.models import ContestParticipation


class Command(BaseCommand):
    help = 'list users with contest participation'

    def add_arguments(self, parser):
        parser.add_argument('users', type=str, help='file with usernames (one per line)')

    def handle(self, *args, **options):
        users_file = options['users']

        with open(users_file) as usernames:
            for username in usernames:
                username = username.strip()

                count = ContestParticipation.objects.filter(user__user__username=username).count()
                if count > 0:
                    self.stdout.write(username)
