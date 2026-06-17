from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import OpenApiTypes, extend_schema

from accounts.permissions import IsAgentOrAdmin, IsClient
from notifications.services import create_notification

from .models import Conversation, Message
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)


class ConversationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ConversationCreateSerializer
        return ConversationSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Conversation.objects.select_related("client", "agent").prefetch_related("messages")
        if user.is_client:
            return qs.filter(client=user)
        if user.is_agent:
            return qs.filter(agent=user) | qs.filter(status=Conversation.Status.OPEN)
        return qs

    def perform_create(self, serializer):
        if not self.request.user.is_client:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les clients peuvent ouvrir une conversation.")
        conversation = serializer.save(client=self.request.user)
        conversation.assign_agent()
        if conversation.agent:
            create_notification(
                conversation.agent,
                "Nouvelle conversation support",
                f"{self.request.user.username} a ouvert une conversation : {conversation.subject}",
                "chat_new",
                {"conversation_id": conversation.id},
            )


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Conversation.objects.select_related("client", "agent")
        if user.is_client:
            return qs.filter(client=user)
        return qs


class ConversationAssignView(APIView):
    permission_classes = [IsAgentOrAdmin]
    serializer_class = ConversationSerializer

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses={200: ConversationSerializer},
    )
    def post(self, request, pk):
        try:
            conversation = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        agent_id = request.data.get("agent_id", request.user.id)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            agent = User.objects.get(pk=agent_id, role__in=[User.Role.AGENT, User.Role.ADMIN])
        except User.DoesNotExist:
            return Response({"detail": "Agent introuvable."}, status=status.HTTP_404_NOT_FOUND)
        conversation.assign_agent(agent)
        return Response(ConversationSerializer(conversation).data)


class ConversationCloseView(APIView):
    permission_classes = [IsAgentOrAdmin]
    serializer_class = ConversationSerializer

    @extend_schema(
        request=None,
        responses={200: ConversationSerializer},
    )
    def post(self, request, pk):
        try:
            conversation = Conversation.objects.get(pk=pk)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation introuvable."}, status=status.HTTP_404_NOT_FOUND)
        conversation.status = Conversation.Status.CLOSED
        conversation.closed_at = timezone.now()
        conversation.save()
        return Response(ConversationSerializer(conversation).data)


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        conversation_id = self.kwargs["pk"]
        return Message.objects.filter(conversation_id=conversation_id).select_related("sender")

    def perform_create(self, serializer):
        conversation_id = self.kwargs["pk"]
        conversation = Conversation.objects.get(pk=conversation_id)
        user = self.request.user
        if user.is_client and conversation.client != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Accès refusé.")
        message = serializer.save(conversation=conversation, sender=user)
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=["updated_at"])

        recipient = conversation.agent if user == conversation.client else conversation.client
        if recipient:
            create_notification(
                recipient,
                "Nouveau message",
                f"Nouveau message dans la conversation : {conversation.subject}",
                "chat_message",
                {"conversation_id": conversation.id},
            )
