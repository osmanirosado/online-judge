import os
import zipfile

from django.core.management.base import BaseCommand
from django.db.models import F

from judge.models import ContestSubmission


class Command(BaseCommand):
    help = "exports all finally accepted contest's submissions"

    def add_arguments(self, parser):
        parser.add_argument('code', help='contest code')
        parser.add_argument('work_dir', help='working directory')
        parser.add_argument('-a', '--all', action='store_true', help='output all submissions')

    def handle(self, *args, **options):
        contest_code = options['code']
        work_dir = options['work_dir']

        cont_sub = ContestSubmission.objects.filter(participation__contest__key=contest_code, participation__virtual=0)
        cont_sub = cont_sub.annotate(
            user=F('submission__user__user__username'),
            cod_problem=F('submission__problem__code'),
            sub_id=F('submission__id'),
            source=F('submission__source__source'),
            ext=F('submission__language__key')
        ).values('user', 'cod_problem', 'points', 'sub_id', 'source', 'ext').order_by('-points')

        def build_path(user, cod_problem, sub_id, ext):
            return os.path.join(user, cod_problem, f"{sub_id}.{ext}")

        def encode_source(src):
            return src.encode('utf-8').strip()

        name = contest_code + '_' + ('all' if options['all'] else 'ok')
        file_path = os.path.join(work_dir, name + '.zip')
        with zipfile.ZipFile(str(file_path), "w", zipfile.ZIP_DEFLATED) as file:
            if options['all']:
                for t in cont_sub:
                    path = build_path(t['user'], t['cod_problem'], t['sub_id'], t['ext'])
                    data = encode_source(t['source'])
                    file.writestr(path, data)
            else:
                user_points = []
                prob_id = {}
                prob_count = 0

                for t in cont_sub:
                    if t['cod_problem'] not in prob_id:
                        user_points.append({})
                        prob_id[t['cod_problem']] = prob_count
                        prob_count += 1

                    act_id = prob_id[t['cod_problem']]

                    if t['user'] not in user_points[act_id]:
                        user_points[act_id][t['user']] = t['points']

                    if t['points'] == user_points[act_id][t['user']]:
                        path = build_path(t['user'], t['cod_problem'], t['sub_id'], t['ext'])
                        data = encode_source(t['source'])
                        file.writestr(path, data)
