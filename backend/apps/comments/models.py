from django.core.validators import RegexValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Comment(MPTTModel):
    author_name = models.CharField(
        max_length=64, validators=[RegexValidator(r'^[A-Za-z0-9]+$', 'Latin letters and digits only.')],
    )
    author_email = models.EmailField()
    author_homepage = models.URLField(blank=True)
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children',
        on_delete=models.CASCADE, db_index=True,
    )
    text = models.TextField()
    text_raw = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class MPTTMeta:
        order_insertion_by = ['-created_at']  # LIFO

    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author_name']),
            models.Index(fields=['author_email']),
        ]

    def __str__(self):
        return f'#{self.pk}'


def upload_to(instance, filename):
    return f'attachments/{instance.comment_id}/{filename}'


class Attachment(models.Model):
    KIND_IMAGE = 'image'
    KIND_TEXT = 'text'
    KIND_CHOICES = [(KIND_IMAGE, 'Image'), (KIND_TEXT, 'Text')]

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='attachments')
    kind = models.CharField(max_length=8, choices=KIND_CHOICES)
    file = models.FileField(upload_to=upload_to)
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
