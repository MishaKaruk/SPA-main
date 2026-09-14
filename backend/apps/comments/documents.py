from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Comment


@registry.register_document
class CommentDocument(Document):
    author_name = fields.KeywordField()
    author_email = fields.KeywordField()
    parent_id = fields.IntegerField()

    class Index:
        name = 'comments'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Comment
        fields = ('text_raw', 'created_at', 'is_deleted')

    def prepare_parent_id(self, instance):
        return instance.parent_id
