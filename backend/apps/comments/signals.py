from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .cache import bump
from .models import Comment
from .serializers import CommentSerializer
from .tasks import index_comment


@receiver(post_save, sender=Comment)
def broadcast(sender, instance, created, **kwargs):
    if not created:
        return
    # deferred so attachments created in the same transaction make it into the payload
    transaction.on_commit(lambda: send(instance))
    transaction.on_commit(lambda: index_comment.delay(instance.pk))
    transaction.on_commit(bump)


def send(instance):
    layer = get_channel_layer()
    if layer is None:
        return
    payload = CommentSerializer(instance, context={'request': None}).data
    async_to_sync(layer.group_send)(
        'comments_root', {'type': 'comment.created', 'payload': payload},
    )
    if instance.parent_id:
        async_to_sync(layer.group_send)(
            f'comments_thread_{instance.get_root().pk}',
            {'type': 'comment.created', 'payload': payload},
        )
