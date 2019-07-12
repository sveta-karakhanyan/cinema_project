from collections import OrderedDict

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from apps.task.models import Room, Film, Seance, Booking, Reserve, Seat


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

    class Meta:
        model = Room
        fields = ('room_name', )


class SeatSerializer(serializers.ModelSerializer):
    row = serializers.IntegerField(required=True, allow_null=False)
    column = serializers.IntegerField(required=True, allow_null=False)
    room = RoomSerializer(many=False)

    class Meta:
        model = Seat
        fields = ('row', 'column', 'room', )


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
        seats = Seat.objects.filter(room=instance.room.id)
        if seats.exists:
            for seat_instance in seats:
                booking = Booking.objects.filter(seat=seat_instance.id, seance=instance.id).first()
                chairs[seat_instance.id] = True if booking else False

        response['chairs'] = chairs
        return response

    class Meta:
        model = Seance
        fields = ('id', 'date', 'start_time', 'room', 'film', )


class BookingSerializer(serializers.ModelSerializer):
    seat = SeatSerializer(many=False)
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

        attrs['user'] = self.context['request'].user
        return attrs

    def create(self, validated_data):
        instance, _ = Booking.objects.get_or_create(**validated_data)
        return instance

    class Meta:
        model = Booking
        fields = ('id', 'seat', 'seance', )


class ReserveSerializer(serializers.ModelSerializer):
    seat = SeatSerializer(many=False)
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

        return attrs

    class Meta:
        model = Reserve
        fields = ('seat', 'seance', )
