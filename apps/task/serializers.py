from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail

from apps.task.models import Cinema, Room, Film, Seans, Booking


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=30, required=True,
                                     validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(required=True, trim_whitespace=True, write_only=True)
    email = serializers.EmailField(required=False)

    def save(self, **kwargs):
        kwargs['password'] = make_password(self.validated_data['password'])
        super().save(**kwargs)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')


class CinemaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cinema
        fields = ('name', )


class RoomSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['cinema'] = CinemaSerializer(instance.cinema).data
        return response

    class Meta:
        model = Room
        fields = ('room_name', 'row_count', 'column_count', 'cinema')


class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = ('name', 'duration')


class SeansSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['room'] = RoomSerializer(instance.room).data
        response['film'] = FilmSerializer(instance.film).data
        return response

    class Meta:
        model = Seans
        fields = ('id', 'date', 'start_time', 'end_time', 'room', 'film')


class BookingSerializer(serializers.ModelSerializer):
    row = serializers.IntegerField(required=True)
    column = serializers.IntegerField(required=True)
    active = serializers.BooleanField(required=True)
    reserve = serializers.BooleanField(required=False, default=0)

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user

        booking = Booking.objects.filter(
            row=attrs['row'], column=attrs['column'], seans=attrs['seans'],
            active=attrs['active']).first()

        if booking and attrs['active']:
            if booking.user_id == attrs['user'].id:
                raise ValidationError({'error_message': 'Have already booked that seat'})
            else:
                reserved_booking = Booking.objects.filter(
                    row=attrs['row'], column=attrs['column'], seans=attrs['seans'],
                    active=0, reserve=1, user=attrs['user'].id).first()

                if reserved_booking:
                    raise ValidationError({'error_message': 'Have already reserved that seat'})

                attrs['reserve'] = 1
                attrs['active'] = 0
        elif booking and attrs['active'] == 0:
            reserved = Booking.objects.filter(
                row=attrs['row'], column=attrs['column'], seans=attrs['seans'],
                active=0, reserve=1
            ).first()

            if reserved:
                send_mail(
                    'Cinema Booking',
                    'You can booking your reserve seat',
                    'from@example.com',
                    [reserved.user.email],
                    fail_silently=False,
                )

        return attrs

    class Meta:
        model = Booking
        fields = ('row', 'column', 'reserve', 'active', 'seans', )
