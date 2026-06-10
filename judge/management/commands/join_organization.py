from django.core.management import BaseCommand

from judge.models import Organization, Profile


class Command(BaseCommand):
    help = 'join organization'

    def add_arguments(self, parser):
        parser.add_argument('users_file', type=str, help='file with usernames (one per line)')
        parser.add_argument('organizations_file', type=str, help='file with organizations (one per line)')

    def handle(self, *args, **options):
        users_file = options['users_file']
        organizations_file = options['organizations_file']

        count = 0
        with open(users_file) as usernames, open(organizations_file) as organizations:
            for username, organization in zip(usernames, organizations):
                username = username.strip()
                short_name = organization.strip()

                try:
                    organization = Organization.objects.get(short_name=short_name)
                    profile = Profile.objects.get(user__username=username)
                    profile.organizations.add(organization)
                    count += 1
                except Organization.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Organization {short_name} does not exist.'))
                except Profile.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User profile {username} does not exist.'))

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} users.'))
