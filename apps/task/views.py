from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import get_user_model

from apps.task.models import Cinema, Seans, Film, Booking
from apps.task.serializers import UserSerializer, CinemaSerializer, SeansSerializer, FilmSerializer, BookingSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['post', ]


class FilmViewSet(ListModelMixin, GenericViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    http_method_names = ['get', ]


class CinemaListViewSet(ListModelMixin, GenericViewSet):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer
    http_method_names = ['get', ]


class SeansViewSet(ListModelMixin, RetrieveModelMixin,  GenericViewSet):
    queryset = Seans.objects.all()
    serializer_class = SeansSerializer
    http_method_names = ['get', ]


class BookingViewSet(ListModelMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    http_method_names = ['get', 'post', 'patch', ]

    def get_queryset(self):
        if self.request.method in ['GET', ]:
            seans = self.request.query_params.get('seans_id', None)
            if seans is not None:
                return self.queryset.filter(seans=seans)
        elif self.request.method in ['POST', ]:
            return self.request.filter(user=self.request.user)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action == 'list':
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]