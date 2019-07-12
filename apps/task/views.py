from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import get_user_model

from apps.task.mixins import UnbookedDestroyModelMixin
from apps.task.models import Seance, Film, Booking, Reserve
from apps.task.serializers import UserSerializer, SeanceSerializer, FilmSerializer, BookingSerializer, ReserveSerializer

User = get_user_model()


class UserViewSet(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['post', ]
    permission_classes = (AllowAny, )


class FilmViewSet(ListModelMixin, GenericViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    http_method_names = ['get', ]


class SeanceViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Seance.objects.all()
    serializer_class = SeanceSerializer
    http_method_names = ['get', ]
    permission_classes = [AllowAny, ]
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('film_id', )


class BookingViewSet(ListModelMixin, CreateModelMixin, UpdateModelMixin, UnbookedDestroyModelMixin, GenericViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', ]
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('seance_id', )

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()

        if self.request.method in ['PATCH', ]:
            kwargs['partial'] = True
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        if self.request.method in ['PATCH', 'DELETE', ]:
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action == 'list':
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]


class ReserveViewSet(CreateModelMixin, GenericViewSet):
    queryset = Reserve.objects.all()
    serializer_class = ReserveSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['post', ]
