from collections import OrderedDict

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from apps.task.models import Room, Film, Seance, Booking, Reserve


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=30, required=True,
                                     validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(required=True, trim_whitespace=True, write_only=True)
    email = serializers.EmailField(max_length=30, required=True,
                                   validators=[UniqueValidator(queryset=User.objects.all())])

    def save(self, **kwargs):
        kwargs['password'] = make_password(self.validated_data['password'])
        super().save(**kwargs)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')


class RoomSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(required=True, allow_blank=False, allow_null=False, max_length=30, min_length=2)
    row_count = serializers.IntegerField(required=True, allow_null=False)
    column_count = serializers.IntegerField(required=True, allow_null=False)

    class Meta:
        model = Room
        fields = ('room_name', 'row_count', 'column_count', )


class FilmSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False, allow_null=False, max_length=30, min_length=2)
    duration = serializers.TimeField(required=True, allow_null=False)

    class Meta:
        model = Film
        fields = ('id', 'name', 'duration')


class SeanceSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True)
    start_time = serializers.TimeField(required=True, allow_null=False)
    room = RoomSerializer(many=False)
    film = FilmSerializer(many=False)

    # TODO: In the body of the response of each seance, add the list of all chairs with boolean value telling whether it is already booked or not. {(row, column): true,}
    def to_representation(self, instance):
        response = super().to_representation(instance)

        chairs = OrderedDict()
        for row in range(1, instance.room.row_count + 1):
            for column in range(1, instance.room.column_count + 1):
                booking = Booking.objects.filter(row=row, column=column, seance=instance.id).first()
                key = (row, column)
                chairs[', '.join(map(str, key))] = True if booking else False

        response['chairs'] = chairs
        return response

    class Meta:
        model = Seance
        fields = ('id', 'date', 'start_time', 'room', 'film', )


class BookingSerializer(serializers.ModelSerializer):
    row = serializers.IntegerField(required=True)
    column = serializers.IntegerField(required=True)
    seance = SeanceSerializer(many=False)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['seance'] = SeanceSerializer(instance.seance).data
        return response

    def validate(self, attrs):
        if not self.partial:
            exists_booking = Booking.objects.filter(**attrs).first()
            if exists_booking:
                raise ValidationError({'error_message': 'Have already booked that seat'})

            seance = Seance.objects.filter(pk=attrs['seance'].id).first()
            if attrs['row'] not in range(1, seance.room.row_count + 1) or \
                    attrs['column'] not in range(1, seance.room.column_count + 1):
                raise ValidationError({'error_message': 'Invalid seat'})

        attrs['user'] = self.context['request'].user
        return attrs

    def create(self, validated_data):
        instance, _ = Booking.objects.get_or_create(**validated_data)
        return instance

    class Meta:
        model = Booking
        fields = ('id', 'row', 'column', 'seance', )


class ReserveSerializer(serializers.ModelSerializer):
    row = serializers.IntegerField(required=True, allow_null=False)
    column = serializers.IntegerField(required=True, allow_null=False)
    seance = SeanceSerializer(many=False)
    # TODO: Add seance here, also validate etc...

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        exists_reserve = Reserve.objects.filter(**attrs).first()
        if exists_reserve:
            raise ValidationError({'error_message': 'Have already reserved that seat'})

        exists_booking = Booking.objects.filter(**attrs).first()
        if exists_booking:
            raise ValidationError({'error_message': 'Have already booked that seat, not necessary to reserve it'})

        seance = Seance.objects.filter(pk=attrs['seance'].id).first()
        if attrs['row'] not in range(1, seance.room.row_count + 1) or \
                attrs['column'] not in range(1, seance.room.column_count + 1):
            raise ValidationError({'error_message': 'Invalid seat'})

        return attrs

    class Meta:
        model = Reserve
        fields = ('row', 'column', 'seance', )
