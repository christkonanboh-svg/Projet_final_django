from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .permissions import IsAdminUser
from .serializers import (
    AdminUserCreateSerializer,
    OnlineStatusSerializer,
    RegisterSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    filterset_fields = ["role", "region"]


class AdminUserCreateView(generics.CreateAPIView):
    serializer_class = AdminUserCreateSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()


@extend_schema(responses={200: UserSerializer(many=True)})
class OnlineAgentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        agents = User.objects.filter(
            role__in=[User.Role.AGENT, User.Role.ADMIN],
            is_online=True,
        )
        return Response(UserSerializer(agents, many=True).data)


class SetOnlineStatusView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OnlineStatusSerializer

    def post(self, request):
        is_online = request.data.get("is_online", True)
        request.user.is_online = bool(is_online)
        request.user.save(update_fields=["is_online"])
        return Response({"is_online": request.user.is_online})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            return Response({"detail": "Les deux champs sont requis."}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({"detail": "Le mot de passe doit contenir au moins 6 caractères."}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.check_password(old_password):
            return Response({"detail": "Ancien mot de passe incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new_password)
        request.user.save()
        return Response({"detail": "Mot de passe modifié avec succès."})
