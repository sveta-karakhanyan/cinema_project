from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail as django_send_email

from apps.task.models import Room, Film, Seans, Booking, Reserve


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
    def to_representation(self, instance):
        response = super().to_representation(instance)
        return response

    class Meta:
        model = Room
        fields = ('room_name', 'row_count', 'column_count', )


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = ('id', 'name', 'duration')


class SeansSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['room'] = RoomSerializer(instance.room).data
        response['film'] = FilmSerializer(instance.film).data
        return response

    class Meta:
        model = Seans
        fields = ('id', 'date', 'start_time', 'end_time', 'room', 'film', )


class BookingSerializer(serializers.ModelSerializer):
    row = serializers.IntegerField(required=True)
    column = serializers.IntegerField(required=True)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['seans'] = SeansSerializer(instance.seans).data
        return response

    def validate(self, attrs):
        if not self.partial:
            exists_booking = Booking.objects.filter(**attrs).first()
            if exists_booking:
                raise ValidationError({'error_message': 'Have already booked that seat'})

            seans = Seans.objects.filter(pk=attrs['seans'].id).first()
            if attrs['row'] not in range(1, seans.room.row_count + 1) or \
                    attrs['column'] not in range(1, seans.room.column_count + 1):
                raise ValidationError({'error_message': 'Invalid seat'})

        attrs['user'] = self.context['request'].user
        return attrs

    def create(self, validated_data):
        instance, _ = Booking.objects.get_or_create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        booking, deleted = Booking.objects.get(pk=instance.id).delete()

        if deleted:
            reserved_users = Reserve.objects.filter(
                row=instance.row, column=instance.column, seans=instance.seans
            ).values_list('id', 'user__username')

            for key, value in reserved_users:
                send_mail = django_send_email(
                    'Cinema Booking',
                    'You can booking your reserve seat',
                    'from@example.com',
                    [value],
                    fail_silently=False,
                )

                if send_mail:
                    Reserve.objects.get(pk=key).delete()

        return []

    class Meta:
        model = Booking
        fields = ('id', 'row', 'column', 'seans', )


class ReserveSerializer(serializers.ModelSerializer):
    row = serializers.IntegerField(required=True)
    column = serializers.IntegerField(required=True)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['seans'] = SeansSerializer(instance.seans).data
        return response

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        exists_reserve = Reserve.objects.filter(**attrs).first()
        if exists_reserve:
            raise ValidationError({'error_message': 'Have already reserved that seat'})

        exists_booking = Booking.objects.filter(**attrs).first()
        if exists_booking:
            raise ValidationError({'error_message': 'Have already booked that seat, not necessary to reserve it'})

        seans = Seans.objects.filter(pk=attrs['seans'].id).first()
        if attrs['row'] not in range(1, seans.room.row_count + 1) or \
                attrs['column'] not in range(1, seans.room.column_count + 1):
            raise ValidationError({'error_message': 'Invalid seat'})

        return attrs

    class Meta:
        model = Reserve
        fields = ('row', 'column', 'seans', )
