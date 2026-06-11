from django.core.management import BaseCommand

from judge.models import Profile


class Command(BaseCommand):
    help = 'override username display'

    def add_arguments(self, parser):
        parser.add_argument('users_file', type=str, help='file with usernames (one per line)')

    def handle(self, *args, **options):
        users_file = options['users_file']

        count = 0
        with open(users_file) as usernames:
            for username in usernames:
                username = username.strip()

                try:
                    profile = Profile.objects.get(user__username=username)
                    profile.is_unlisted = False
                    profile.save()
                    count += 1
                except Profile.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User profile {username} does not exist.'))

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} users.'))
