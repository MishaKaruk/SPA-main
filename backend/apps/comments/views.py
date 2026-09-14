from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.core.cache import cache
from elastic_transport import TransportError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import TTL, generation
from .documents import CommentDocument
from .models import Comment
from .sanitize import InvalidXHTML, sanitize
from .serializers import CommentCreateSerializer, CommentSerializer


# comments are never edited or removed through the API, so the write side is create only
class CommentViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    ordering_fields = ['created_at', 'author_name', 'author_email']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Comment.objects.prefetch_related('attachments')
        if self.action == 'list':
            qs = qs.filter(parent__isnull=True)
        return qs.filter(is_deleted=False)

    def get_serializer_class(self):
        return CommentCreateSerializer if self.action == 'create' else CommentSerializer

    def list(self, request, *args, **kwargs):
        ordering = request.query_params.get('ordering', '')
        if ordering.lstrip('-') not in self.ordering_fields:
            ordering = ''
        # the host is part of the key: cached payloads carry absolute attachment URLs
        key = (
            f'comments:roots:{generation()}:{request.get_host()}'
            f":{ordering}:{request.query_params.get('page', '1')}"
        )
        data = cache.get(key)
        if data is None:
            data = super().list(request, *args, **kwargs).data
            cache.set(key, data, TTL)
        return Response(data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({'detail': 'q is required.'}, status=status.HTTP_400_BAD_REQUEST)
        hits = (
            CommentDocument.search()
            .filter('term', is_deleted=False)
            .query('multi_match', query=q, fields=['text_raw', 'author_name'])[:25]
        )
        try:
            ids = [int(h.meta.id) for h in hits]
        except TransportError:
            return Response({'detail': 'Search is unavailable.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        found = {c.pk: c for c in Comment.objects.filter(pk__in=ids).prefetch_related('attachments')}
        ordered = [found[i] for i in ids if i in found]
        return Response(CommentSerializer(ordered, many=True, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def tree(self, request, pk=None):
        root = self.get_object()
        key = f'comments:tree:{generation()}:{request.get_host()}:{root.pk}'
        data = cache.get(key)
        if data is None:
            nodes = root.get_descendants(include_self=True).prefetch_related('attachments')
            data = CommentSerializer(nodes, many=True, context={'request': request}).data
            cache.set(key, data, TTL)
        return Response(data)


class PreviewView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            html = sanitize(request.data.get('text', ''))
        except InvalidXHTML as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'html': html})


@api_view(['GET'])
@permission_classes([AllowAny])
def captcha_new(request):
    key = CaptchaStore.generate_key()
    return Response({
        'key': key,
        'image_url': request.build_absolute_uri(captcha_image_url(key)),
    })
