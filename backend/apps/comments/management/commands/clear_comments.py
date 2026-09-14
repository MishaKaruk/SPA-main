from pathlib import Path

from captcha.models import CaptchaStore
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from elastic_transport import TransportError

from apps.comments.cache import bump
from apps.comments.documents import CommentDocument
from apps.comments.models import Attachment, Comment


class Command(BaseCommand):
    help = 'Remove every comment, its attachments, the files behind them and expired captchas.'

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_true', help='skip the confirmation')

    def handle(self, *args, **options):
        total = Comment.objects.count()
        if not total:
            self.stdout.write('Nothing to remove.')
            return
        if not options['noinput'] and input(f'Remove {total} comments and their files? [y/N] ').lower() != 'y':
            self.stdout.write('Cancelled.')
            return

        files = 0
        for att in Attachment.objects.all():
            att.file.delete(save=False)
            files += 1
        Comment.objects.all().delete()

        uploads = Path(settings.MEDIA_ROOT) / 'attachments'
        for d in sorted(uploads.glob('*'), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()

        try:
            CommentDocument.search().query('match_all').delete()
        except TransportError:
            self.stderr.write('Search index left untouched: the cluster is unreachable.')
        bump()

        captchas = CaptchaStore.objects.count()
        call_command('captcha_clean', verbosity=0)
        expired = captchas - CaptchaStore.objects.count()
        self.stdout.write(f'Removed {total} comments, {files} files and {expired} expired captchas.')
