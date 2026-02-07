from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'change passwords'

    def add_arguments(self, parser):
        parser.add_argument('users_file', type=str, help='file with usernames (one per line)')
        parser.add_argument('passwords_file', type=str, help='file with passwords (one per line)')

    def handle(self, *args, **options):
        users_file = options['users_file']
        passwords_file = options['passwords_file']

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
                    self.stdout.write(self.style.ERROR('User %s does not exist' % username))

        self.stdout.write(self.style.SUCCESS('Successfully changed passwords of %d users' % count))
