from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'rename usernames'

    def add_arguments(self, parser):
        parser.add_argument('old_usernames_file', type=str, help='file with old usernames (one per line)')
        parser.add_argument('new_usernames_file', type=str, help='file with new usernames (one per line)')

    def handle(self, *args, **options):
        old_usernames_file = options['old_usernames_file']
        new_usernames_file = options['new_usernames_file']

        count = 0
        with open(old_usernames_file) as old_usernames, open(new_usernames_file) as new_usernames:
            for old_username, new_username in zip(old_usernames, new_usernames):
                old_username = old_username.strip()
                new_username = new_username.strip()
                try:
                    usr = User.objects.get(username=old_username)
                    usr.username = new_username
                    usr.save()
                    count += 1
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User {old_username} does not exist'))

        self.stdout.write(self.style.SUCCESS(f'Successfully changed passwords of {count} users.'))
