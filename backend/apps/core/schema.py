import graphene
from graphene_django import DjangoObjectType

from apps.comments.models import Comment


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ('id', 'parent', 'text', 'created_at', 'author_name', 'author_email', 'author_homepage')


class Query(graphene.ObjectType):
    roots = graphene.List(CommentType, limit=graphene.Int(default_value=25))
    thread = graphene.List(CommentType, root_id=graphene.Int(required=True))

    def resolve_roots(root, info, limit):
        return (
            Comment.objects.filter(parent__isnull=True, is_deleted=False)
            .order_by('-created_at')[:limit]
        )

    def resolve_thread(root, info, root_id):
        node = Comment.objects.filter(pk=root_id).first()
        if not node:
            return []
        return node.get_descendants(include_self=True)


schema = graphene.Schema(query=Query)
