from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Conversation(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Ouverte"
        ASSIGNED = "assigned", "Assignée"
        CLOSED = "closed", "Fermée"

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_conversations")
    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agent_conversations",
        limit_choices_to={"role__in": [User.Role.AGENT, User.Role.ADMIN]},
    )
    subject = models.CharField(max_length=200, default="Support client")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation #{self.pk} - {self.client.username}"

    def assign_agent(self, agent=None):
        if agent:
            self.agent = agent
        else:
            available = User.objects.filter(
                role__in=[User.Role.AGENT, User.Role.ADMIN],
                is_online=True,
            ).first()
            if available:
                self.agent = available
        if self.agent:
            self.status = self.Status.ASSIGNED
        self.save()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message #{self.pk} de {self.sender.username}"
