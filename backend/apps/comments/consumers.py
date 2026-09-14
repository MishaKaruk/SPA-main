from channels.generic.websocket import AsyncJsonWebsocketConsumer


class CommentsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        tid = self.scope['url_route']['kwargs'].get('thread_id')
        self.group = f'comments_thread_{tid}' if tid else 'comments_root'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def comment_created(self, event):
        await self.send_json({'event': 'comment.created', 'payload': event['payload']})
