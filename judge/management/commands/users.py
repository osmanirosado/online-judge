import random
import string

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from judge.models import *


class Command(BaseCommand):
    help = 'manage contest users (add, change pass, unactivate)'

    @staticmethod
    def get_pass(file, length=10):
        if file:
            return file.readline()
        else:
            letters = string.ascii_lowercase
            return ''.join(random.choice(letters) for i in range(length))
            
    @staticmethod
    def set_active(users_file_name, value):
        count = 0
        with open(users_file_name) as file:
            for name in file:
                usr = User.objects.get(username=name.strip())
                usr.is_active = value
                usr.save()
                count += 1
        
        return count

    def add_arguments(self, parser):
        parser.add_argument('action', help="one of 'add', 'change_pass', 'activate', or 'unactivate'")
        parser.add_argument('file', help='file with usernames (one per line)')
        parser.add_argument('-o', '--organization', help='organization (short name) where created user will be added')
        parser.add_argument('-p', '--pass_file', help=('file for reading passwords (one per line), if not present'
                                                       'random password is generated and written to pass.txt'))

    def handle(self, *args, **options):
        action = options['action']
        users_file_name = options['file']
        pass_file_name = options['pass_file']
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

            if pass_file_name:
                pass_file = open(pass_file_name, "r")
            else:
                pass_file = None
                out_file = open('pass.txt', "w")

            count = 0
            with open(users_file_name) as file:
                for name in file:
                    name = name.strip()
                    usr = User(username=name, email='', is_active=True)

                    passw = Command.get_pass(pass_file).strip()
                    if not pass_file_name:
                        out_file.write(passw + '\n')

                    usr.set_password(passw)
                    usr.is_superuser = False
                    usr.is_staff = False
                    usr.save()

                    profile = Profile(user=usr)
                    profile.language = Language.objects.get(key='CPP20')
                    profile.mute = True
                    profile.save()

                    profile.organizations.add(org)

                    count += 1

            if not pass_file_name:
                out_file.close()
                self.stdout.write(self.style.SUCCESS('Passwords were written to pass.txt'))

            self.stdout.write(self.style.SUCCESS('Successfully added %d users' % count))
        elif action == 'change_pass':
            if not pass_file_name:
                self.stdout.write(self.style.ERROR('You must provide pass file'))
                return

            pass_file = open(pass_file_name, "r")
            count = 0
            with open(users_file_name) as file:
                for name in file:
                    passw = Command.get_pass(pass_file).strip()
                    usr = User.objects.get(username=name.strip())
                    usr.set_password(passw)
                    usr.save()
                    count += 1
            self.stdout.write(self.style.SUCCESS('Successfully changed passwords of %d users' % count))
        elif action == 'activate':
            count = Command.set_active(users_file_name, True)
            self.stdout.write(self.style.SUCCESS('Successfully activated %d users' % count))
        elif action == 'unactivate':
            count = Command.set_active(users_file_name, False)
            self.stdout.write(self.style.SUCCESS('Successfully unactivated %d users' % count))
        else:
            self.stdout.write(self.style.ERROR('Unrecognized action "%s"' % action))
