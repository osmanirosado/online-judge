from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'change passwords'

    def add_arguments(self, parser):
        parser.add_argument('users', type=str, help='file with usernames (one per line)')
        parser.add_argument('passwords', type=str, help='file with passwords (one per line)')

    def handle(self, *args, **options):
        users_file = options['users']
        passwords_file = options['passwords']

        count = 0
        with open(users_file) as usernames, open(passwords_file) as passwords:
            for username, password in zip(usernames, passwords):
                username = username.strip()
                password = password.strip()
                try:
                    usr = User.objects.get(username=username)
                    usr.set_password(password)
                    usr.save()
                    count += 1
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User {username} does not exist'))

        self.stdout.write(self.style.SUCCESS(f'Successfully changed passwords of {count} users.'))
