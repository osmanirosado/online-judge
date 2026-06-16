from django.core.management import BaseCommand

from judge.models import Profile


class Command(BaseCommand):
    help = 'override username display'

    def add_arguments(self, parser):
        parser.add_argument('users', type=str, help='file with usernames (one per line)')
        parser.add_argument('names', type=str, help='file with full names (one per line)')

    def handle(self, *args, **options):
        users_file = options['users']
        names_file = options['names']

        count = 0
        with open(users_file) as usernames, open(names_file) as names:
            for username, name in zip(usernames, names):
                username = username.strip()
                name = name.strip()

                try:
                    profile = Profile.objects.get(user__username=username)
                    profile.username_display_override = name
                    profile.save()
                    count += 1
                except Profile.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User profile {username} does not exist.'))

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} users.'))
