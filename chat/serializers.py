from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)
    sender_role = serializers.CharField(source="sender.role", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_name",
            "sender_role",
            "content",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "sender", "is_read", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    client_detail = UserSerializer(source="client", read_only=True)
    agent_detail = UserSerializer(source="agent", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.IntegerField(source="messages.count", read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "client",
            "client_detail",
            "agent",
            "agent_detail",
            "subject",
            "status",
            "status_display",
            "last_message",
            "message_count",
            "created_at",
            "updated_at",
            "closed_at",
        ]
        read_only_fields = ["id", "client", "agent", "status", "created_at", "updated_at", "closed_at"]

    @extend_schema_field(MessageSerializer)
    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return MessageSerializer(msg).data
        return None


class ConversationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["subject"]


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["content"]
