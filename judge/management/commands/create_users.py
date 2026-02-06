from django.contrib.auth.models import User
from django.core.management import BaseCommand

from judge.models import Profile, Language, Organization


class Command(BaseCommand):
    help = 'create users'

    def add_arguments(self, parser):
        parser.add_argument('organization', type=str, help='organization short name')
        parser.add_argument('users_file', type=str, help='file with usernames (one per line)')

    def handle(self, *args, **options):
        usernames_file = options['users_file']
        organization_short_name = options['organization']

        count = 0
        organization = Organization.objects.get(short_name=organization_short_name)
        with open(usernames_file) as file:
            for username in file:
                user = User.objects.create_user(username=username, is_active=False, is_staff=False, is_superuser=False)
                user.save()

                language = Language.objects.get(key='CPP20')
                user_profile = Profile.objects.create(user=user, language=language, mute=True, site_theme='light')
                user_profile.save()

                user_profile.organizations.add(organization)
                count += 1

        self.stdout.write(self.style.SUCCESS('Successfully created %d users' % count))
