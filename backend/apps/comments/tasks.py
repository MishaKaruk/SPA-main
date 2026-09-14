from celery import shared_task
from elastic_transport import TransportError

from .documents import CommentDocument
from .models import Comment


@shared_task(autoretry_for=(TransportError,), retry_backoff=2, max_retries=6)
def index_comment(comment_id):
    comment = Comment.objects.filter(pk=comment_id).first()
    if comment:
        CommentDocument().update(comment)
