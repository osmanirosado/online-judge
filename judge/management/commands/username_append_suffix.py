from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'username append suffix'

    def add_arguments(self, parser):
        parser.add_argument('suffix', type=str, help='suffix to append')
        parser.add_argument('users', type=str, help='file with usernames (one per line)')

    def handle(self, *args, **options):
        suffix = options['suffix']
        users_file = options['users']

        count = 0
        with open(users_file) as usernames:
            for username in usernames:
                username = username.strip()

                try:
                    user = User.objects.get(username=username)
                    user.username += suffix
                    user.save()
                    count += 1
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User {username} does not exist.'))

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} users.'))
