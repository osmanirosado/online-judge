from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'unused users'

    def add_arguments(self, parser):
        parser.add_argument('users', type=str, help='file with usernames (one per line)')
        parser.add_argument('--negate', dest='value', action='store_false', help='show used users instead of unused ones')

    def handle(self, *args, **options):
        users_file = options['users']
        value = options['value']

        unused_user = lambda u: u.last_login is None
        used_user = lambda u: u.last_login is not None
        show_user = unused_user if value else used_user

        with open(users_file) as usernames:
            for username in usernames:
                username = username.strip()

                try:
                    user = User.objects.get(username=username)
                    if show_user(user):
                        self.stdout.write(user.username)
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
