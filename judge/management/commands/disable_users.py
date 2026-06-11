from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'disable users'

    def add_arguments(self, parser):
        parser.add_argument('users_file', type=str, help='file with usernames (one per line)')

    def handle(self, *args, **options):
        users_file = options['users_file']

        count = 0
        with open(users_file) as usernames:
            for username in usernames:
                username = username.strip()

                try:
                    user = User.objects.get(username=username)
                    user.is_active = False
                    user.save()
                    count += 1
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User {username} does not exist.'))

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} users.'))
