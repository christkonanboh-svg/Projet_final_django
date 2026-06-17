from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        unread = self.request.query_params.get("unread")
        if unread == "true":
            qs = qs.filter(is_read=False)
        return qs


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    @extend_schema(
        request=None,
        responses={200: NotificationSerializer},
    )
    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification introuvable."}, status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(
        request=None,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"detail": f"{count} notification(s) marquée(s) comme lue(s)."})


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})
