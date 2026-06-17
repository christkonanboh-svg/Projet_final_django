import json
import urllib.parse

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from .models import Conversation, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"
        self.user = await self.get_user_from_token()

        if not self.user:
            await self.close()
            return

        has_access = await self.user_has_access()
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_join",
                "user_id": self.user.id,
                "username": self.user.username,
                "is_online": True,
            },
        )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            if self.user:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_join",
                        "user_id": self.user.id,
                        "username": self.user.username,
                        "is_online": False,
                    },
                )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type", "message")

        if message_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_indicator",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "is_typing": data.get("is_typing", False),
                },
            )
            return

        content = data.get("content", "").strip()
        if not content:
            return

        message = await self.save_message(content)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": {
                    "id": message["id"],
                    "content": message["content"],
                    "sender_id": self.user.id,
                    "sender_name": self.user.get_full_name() or self.user.username,
                    "sender_role": self.user.role,
                    "created_at": message["created_at"],
                },
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
        }))

    async def typing_indicator(self, event):
        if event["user_id"] != self.user.id:
            await self.send(text_data=json.dumps({
                "type": "typing",
                "username": event["username"],
                "is_typing": event["is_typing"],
            }))

    async def user_join(self, event):
        if event["user_id"] != self.user.id:
            await self.send(text_data=json.dumps({
                "type": "presence",
                "username": event["username"],
                "is_online": event["is_online"],
            }))

    @database_sync_to_async
    def get_user_from_token(self):
        query_string = self.scope.get("query_string", b"").decode()
        token = None
        for param in query_string.split("&"):
            if param.startswith("token="):
                token = urllib.parse.unquote(param.split("=", 1)[1])
                break
        if not token:
            return None
        try:
            access = AccessToken(token)
            user_id = access["user_id"]
            return User.objects.get(pk=user_id)
        except Exception:
            return None

    @database_sync_to_async
    def user_has_access(self):
        try:
            conversation = Conversation.objects.get(pk=self.conversation_id)
        except Conversation.DoesNotExist:
            return False
        if self.user.is_client:
            return conversation.client_id == self.user.id
        return True

    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(pk=self.conversation_id)
        msg = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content,
        )
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=["updated_at"])
        return {
            "id": msg.id,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        }
