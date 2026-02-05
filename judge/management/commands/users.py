from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from judge.models import *
from judge.models import Organization


class Command(BaseCommand):
    help = 'Manage contest users: add, change password, enable or disable'

    def add_arguments(self, parser):
        parser.add_argument('action', help="one of 'add', 'change_pass', 'enable', or 'disable'")
        parser.add_argument('file', help='file with usernames (one per line)')
        parser.add_argument('-o', '--organization', help='organization (short name) where created user will be added')
        parser.add_argument('-p', '--pass_file', help='file for reading passwords (one per line)')

    def handle(self, *args, **options):
        action = options['action']
        users_file_path = options['file']
        pass_file_path = options['pass_file']
        org = options['organization']

        if action == 'add':
            if not options['organization']:
                self.stdout.write(self.style.ERROR('You must provide an organization.'))
                return

            try:
                org = Organization.objects.get(short_name=org)
            except Organization.DoesNotExist:
                self.stdout.write(self.style.ERROR('Organization with short name "%s" does not exist.' % org))
                return

            if not pass_file_path:
                self.stdout.write(self.style.ERROR('You must provide pass file'))
                return

            count = Command.add_users(users_file_path, pass_file_path, org)
            self.stdout.write(self.style.SUCCESS('Successfully added %d users' % count))
        elif action == 'change_pass':
            if not pass_file_path:
                self.stdout.write(self.style.ERROR('You must provide pass file'))
                return

            count = self.change_passwords(users_file_path, pass_file_path)
            self.stdout.write(self.style.SUCCESS('Successfully changed passwords of %d users' % count))
        elif action == 'enable':
            count = Command.set_active(users_file_path, True)
            self.stdout.write(self.style.SUCCESS('Successfully activated %d users' % count))
        elif action == 'disable':
            count = Command.set_active(users_file_path, False)
            self.stdout.write(self.style.SUCCESS('Successfully unactivated %d users' % count))
        else:
            self.stdout.write(self.style.ERROR('Unrecognized action "%s"' % action))

    @staticmethod
    def add_users(users_file_path, passwords_file_path, org: Organization) -> int:
        count = 0
        with open(users_file_path) as names, open(passwords_file_path) as passwords:
            for name, password in zip(names, passwords):
                Command.add_user(name.strip(), password.strip(), org)
                count += 1
        return count

    @staticmethod
    def add_user(name: str, passw: str, org: Organization):
        user = User(
            username=name,
            email='',
            is_active=False,
            is_superuser=False,
            is_staff=False,
        )
        user.set_password(passw)
        user.save()

        user_profile = Profile(
            user=user,
            mute=True,
            language=Language.objects.get(key='CPP20'),
            site_theme='light',
        )
        user_profile.save()

        user_profile.organizations.add(org)

    @staticmethod
    def change_passwords(users_file_path, passwords_file_path) -> int:
        count = 0
        with open(users_file_path) as names, open(passwords_file_path) as passwords:
            for name, password in zip(names, passwords):
                usr = User.objects.get(username=name.strip())
                usr.set_password(password.strip())
                usr.save()
                count += 1
        return count

    @staticmethod
    def set_active(users_file_path, value: bool):
        count = 0
        with open(users_file_path) as file:
            for name in file:
                usr = User.objects.get(username=name.strip())
                usr.is_active = value
                usr.save()
                count += 1

        return count
