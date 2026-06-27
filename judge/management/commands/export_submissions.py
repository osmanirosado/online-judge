import os
import zipfile

from django.core.management.base import BaseCommand
from django.db.models import F

from judge.models import ContestSubmission


class Command(BaseCommand):
    help = "exports all contest submissions"

    def add_arguments(self, parser):
        parser.add_argument('code', help='contest code')
        parser.add_argument('work_dir', help='working directory')

    def handle(self, *args, **options):
        contest_code = options['code']
        work_dir = options['work_dir']

        contest_submissions = ContestSubmission.objects.filter(
            participation__contest__key=contest_code,
            participation__virtual=0
        ).annotate(
            username=F('submission__user__user__username'),
            problem_code=F('submission__problem__code'),
            submission_source=F('submission__source__source'),
            language_key=F('submission__language__key')
        ).values('username', 'problem_code', 'submission_id', 'submission_source', 'language_key')

        file_name = f"{contest_code}_all.zip"
        file_path = os.path.join(work_dir, file_name)
        self.stdout.write(f'Archiving submissions ...')
        with zipfile.ZipFile(str(file_path), "w", zipfile.ZIP_DEFLATED) as file:
            for submission in contest_submissions:
                username = submission['username']
                problem_code = submission['problem_code']
                submission_id = submission['submission_id']
                submission_source = submission['submission_source']
                language_key = submission['language_key']

                path = os.path.join(username, problem_code, f"{submission_id}.{language_key.lower()}")
                data = submission_source.encode('utf-8').strip()
                file.writestr(str(path), data)
        self.stdout.write(self.style.SUCCESS(f'Successfully exported file: {file_path}'))
