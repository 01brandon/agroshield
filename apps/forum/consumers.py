import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Post, Reply

class ForumConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # join the general forum room
        self.room_group_name = 'forum_general'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data    = json.loads(text_data)
        action  = data.get('action')

        if action == 'new_reply':
            reply = await self.save_reply(data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':      'forum_message',
                    'post_id':   data['post_id'],
                    'author':    data['author'],
                    'body':      data['body'],
                    'is_expert': data.get('is_expert', False),
                }
            )

    async def forum_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_reply(self, data):
        post = Post.objects.get(id=data['post_id'])
        return Reply.objects.create(
            post      = post,
            author    = self.scope['user'],
            body      = data['body'],
            is_expert = data.get('is_expert', False),
        )
