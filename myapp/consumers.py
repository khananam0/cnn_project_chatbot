# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        print(f"room_name==========>: {self.room_name}")
        print(f"room_group_name==========>: {self.room_group_name}")

        # Join the chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"receive data==========>: {data}")
        
        sender_id = data['sender']
        receiver_id = data['receiver']
        content = data['content']

        # Save the message to the database
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        message = Message.objects.create(sender=sender, receiver=receiver, content=content)

        # Send the message to the chat group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': sender.username,
                'receiver': receiver.username,
                'content': content,
                'timestamp': str(message.timestamp),
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'receiver': event['receiver'],
            'content': event['content'],
            'timestamp': event['timestamp'],
        }))
