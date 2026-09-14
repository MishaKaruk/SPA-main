from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Attachment, Comment


@admin.register(Comment)
class CommentAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'author_name', 'created_at', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('text_raw', 'author_name', 'author_email')


admin.site.register(Attachment)
