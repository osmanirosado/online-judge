from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import IntegrityError

from judge.models import Profile, Language


class Command(BaseCommand):
    help = 'create users'

    def add_arguments(self, parser):
        parser.add_argument('users_file', type=str, help='file with usernames (one per line)')

    def handle(self, *args, **options):
        lang_key = 'CPP20'
        language = self.get_language(key=lang_key)
        if language is None:
            self.stdout.write(self.style.ERROR(f'Language {lang_key} does not exist.'))
            return

        usernames_file = options['users_file']

        created = skipped = 0
        with open(usernames_file) as usernames:
            for username in usernames:
                username = username.strip()
                user = self.create_user(username)
                if user is None:
                    skipped += 1
                    continue
                profile = self.create_profile(user, language)
                if profile is None:
                    self.stdout.write(self.style.ERROR(f'Profile creation failed for user: {username}.'))
                    break

                created += 1

        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'Unable to create {skipped} users because they already exist.'))
        if created > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created} users.'))

    @staticmethod
    def get_language(key: str) -> Language | None:
        try:
            language = Language.objects.get(key=key)
            return language
        except Language.DoesNotExist:
            return None

    @staticmethod
    def create_user(username: str) -> User | None:
        try:
            user = User.objects.create_user(username=username, is_active=False, is_staff=False, is_superuser=False)
            user.save()
            return user
        except IntegrityError:
            return None

    @staticmethod
    def create_profile(user: User, language: Language) -> Profile | None:
        try:
            profile = Profile.objects.create(user=user, language=language, site_theme='light')
            profile.save()
            return profile
        except IntegrityError:
            return None
