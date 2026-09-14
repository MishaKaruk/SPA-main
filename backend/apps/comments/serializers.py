from captcha.models import CaptchaStore
from django.conf import settings
from django.db import transaction
from PIL import Image
from rest_framework import serializers

from .identity import issue, read
from .images import EXTENSIONS, fit, stored_name
from .models import Attachment, Comment
from .sanitize import InvalidXHTML, sanitize


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ('id', 'kind', 'url', 'original_name', 'size', 'created_at')

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)
    children_count = serializers.IntegerField(source='get_descendant_count', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id', 'author', 'parent', 'text', 'created_at',
            'attachments', 'children_count',
        )
        read_only_fields = ('id', 'author', 'created_at', 'text')

    def get_author(self, obj):
        return {
            'username': obj.author_name,
            'email': obj.author_email,
            'homepage': obj.author_homepage or None,
        }


class CommentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='author_name', required=False)
    email = serializers.EmailField(source='author_email', required=False)
    homepage = serializers.URLField(source='author_homepage', required=False, allow_blank=True)
    text = serializers.CharField()
    file = serializers.FileField(write_only=True, required=False)
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)
    identity = serializers.CharField(write_only=True, required=False)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id', 'parent', 'username', 'email', 'homepage', 'text', 'file',
            'attachments', 'captcha_key', 'captcha_value', 'identity',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        key = attrs.pop('captcha_key')
        value = attrs.pop('captcha_value').strip().lower()
        store = CaptchaStore.objects.filter(hashkey=key).first()
        if not store or store.response != value:
            raise serializers.ValidationError({'captcha': 'Wrong CAPTCHA.'})
        store.delete()
        known = read(attrs.pop('identity', ''))
        if known and not attrs.get('author_name'):
            attrs['author_name'] = known['name']
            attrs['author_email'] = known['email']
            attrs['author_homepage'] = known['homepage']
        missing = {
            name: 'This field is required.'
            for name, key in (('username', 'author_name'), ('email', 'author_email'))
            if not attrs.get(key)
        }
        if missing:
            raise serializers.ValidationError(missing)
        return attrs

    def validate_username(self, value):
        if not value.isalnum() or not value.isascii():
            raise serializers.ValidationError('Latin letters and digits only.')
        return value

    def validate_text(self, value):
        try:
            return sanitize(value)
        except InvalidXHTML as e:
            raise serializers.ValidationError(str(e))

    def validate_file(self, f):
        self.kind, self.fmt = attachment_kind(f)
        return f

    def create(self, validated_data):
        request = self.context['request']
        f = validated_data.pop('file', None)
        validated_data['text_raw'] = self.initial_data.get('text', '')
        validated_data['ip'] = client_ip(request)
        validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:255]
        with transaction.atomic():
            comment = super().create(validated_data)
            if f:
                name = f.name
                if self.kind == Attachment.KIND_IMAGE:
                    f = fit(f) or f
                    f.name = stored_name(name, EXTENSIONS[self.fmt])
                else:
                    f.name = stored_name(name, 'txt')
                Attachment.objects.create(
                    comment=comment, kind=self.kind, file=f,
                    original_name=name[:255], size=f.size,
                )
        return comment

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['identity'] = issue(instance)
        return data


def attachment_kind(f):
    if f.name.lower().endswith('.txt'):
        if f.size > settings.COMMENTS_MAX_TEXT_FILE_SIZE:
            raise serializers.ValidationError('Text file must not exceed 100 KB.')
        return Attachment.KIND_TEXT, None
    try:
        Image.open(f).verify()
        f.seek(0)
        img = Image.open(f)
        fmt, frames = img.format, getattr(img, 'n_frames', 1)
    except Exception:
        raise serializers.ValidationError('Only JPG, PNG, GIF images and .txt files are allowed.')
    finally:
        f.seek(0)
    if fmt not in settings.COMMENTS_ALLOWED_IMAGE_FORMATS:
        raise serializers.ValidationError(f'{fmt} is not an allowed image format.')
    if frames > settings.COMMENTS_MAX_GIF_FRAMES:
        raise serializers.ValidationError(
            f'Animations are limited to {settings.COMMENTS_MAX_GIF_FRAMES} frames.'
        )
    return Attachment.KIND_IMAGE, fmt


def client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
