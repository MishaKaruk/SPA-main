from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, PreviewView, captcha_new

router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('comments-preview/', PreviewView.as_view(), name='comment-preview'),
    path('captcha/', captcha_new, name='captcha-new'),
]
