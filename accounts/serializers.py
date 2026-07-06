from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    region_display = serializers.CharField(source="get_region_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "cni_number",
            "role",
            "role_display",
            "region",
            "region_display",
            "is_online",
            "date_joined",
        ]
        read_only_fields = ["id", "role", "is_online", "date_joined"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "region", "cni_number"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "region",
            "cni_number",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        from notifications.services import create_notification
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data, role=User.Role.CLIENT)
        user.set_password(password)
        user.save()
        # Notifier les admins de la nouvelle inscription
        admins = User.objects.filter(role=User.Role.ADMIN)
        for admin in admins:
            create_notification(
                admin,
                "Nouveau client inscrit",
                f"{user.get_full_name() or user.username} vient de créer un compte client (CNI: {user.cni_number or 'N/A'}).",
                "new_registration",
                {"user_id": user.id},
            )
        return user


class OnlineStatusSerializer(serializers.Serializer):
    is_online = serializers.BooleanField()


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "cni_number",
            "role",
            "region",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
