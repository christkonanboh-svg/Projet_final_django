from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        AGENT = "agent", "Agent de terrain"
        ADMIN = "admin", "Administrateur"

    class Region(models.TextChoices):
        ABIDJAN = "abidjan", "Abidjan"
        BOUAKE = "bouake", "Bouaké"
        SAN_PEDRO = "san_pedro", "San-Pédro"
        KORHOGO = "korhogo", "Korhogo"
        YAMOUSSOUKRO = "yamoussoukro", "Yamoussoukro"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=30, choices=Region.choices, blank=True)
    is_online = models.BooleanField(default=False)
    cni_number = models.CharField(max_length=20, blank=True, default="", verbose_name="Numéro CNI")

    class Meta:
        ordering = ["username"]

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_agent(self):
        return self.role == self.Role.AGENT

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
