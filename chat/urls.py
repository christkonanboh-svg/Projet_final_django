from django.urls import path

from .views import (
    ConversationAssignView,
    ConversationCloseView,
    ConversationDetailView,
    ConversationListCreateView,
    MessageListCreateView,
)

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="chat-conversations"),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(), name="chat-conversation-detail"),
    path("conversations/<int:pk>/assign/", ConversationAssignView.as_view(), name="chat-conversation-assign"),
    path("conversations/<int:pk>/close/", ConversationCloseView.as_view(), name="chat-conversation-close"),
    path("conversations/<int:pk>/messages/", MessageListCreateView.as_view(), name="chat-messages"),
]
