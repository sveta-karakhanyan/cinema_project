from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail as django_send_email

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

    def to_internal_value(self, data):
        cinema_id = data.get('cinema')
        if cinema_id is not None and Cinema.objects.filter(pk=cinema_id).exists():
            raise ValidationError({"error_message": 'Cinema does not exists'})

    class Meta:
        model = Room
        fields = ('room_name', 'row_count', 'column_count', 'cinema')


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

    def to_internal_value(self, data):
        room_id = data.get('room')
        film_id = data.get('film')
        if room_id is not None and not Room.objects.filter(pk=room_id).exists():
            raise ValidationError({'error_message': 'Room does not exists'})
        if film_id is not None and not Film.objects.filter(pk=film_id).exists():
            raise ValidationError({'error_message': 'Film does not exists'})
        return super().to_internal_value(data)

    class Meta:
        model = Seans
        fields = ('id', 'date', 'start_time', 'end_time', 'room', 'film', )


class BookingSerializer(serializers.ModelSerializer):
    row = serializers.IntegerField(required=True)
    column = serializers.IntegerField(required=True)
    active = serializers.BooleanField(required=True)
    reserve = serializers.BooleanField(required=False, default=False)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['seans'] = SeansSerializer(instance.seans).data
        return response

    def to_internal_value(self, data):
        seans_id = data.get('seans')
        if seans_id is not None and not Seans.objects.filter(pk=seans_id).exists():
            raise ValidationError({'error_message': 'Seans does not exists'})
        return super().to_internal_value(data)

    def create(self, validated_data):
        exists_booking = Booking.objects.filter(
            row=validated_data['row'], column=validated_data['column'],
            seans=validated_data['seans'],
            user=validated_data['user'],
        ).first()

        if exists_booking:
            return exists_booking

        if validated_data['active']:
            return Booking.objects.create(
                row=validated_data['row'], column=validated_data['column'],
                seans=validated_data['seans'], active=1,
                user=validated_data['user'], reserve=0
            )
        elif 'reserve' in validated_data:
            return Booking.objects.create(
                row=validated_data['row'], column=validated_data['column'],
                seans=validated_data['seans'], active=0,
                user=validated_data['user'], reserve=1
            )

    def validate(self, attrs):
        if 'reserve' in attrs:
            if (attrs['active'] and attrs['reserve']) or (attrs['active'] == 0 and attrs['reserve'] == 0):
                raise ValidationError({'error_message': 'Cannot save - reserve or book seat'})

        exists_booking = Booking.objects.filter(**attrs).first()
        attrs['user'] = self.context['request'].user

        if not self.partial:
            if exists_booking and attrs['active']:
                raise ValidationError({'error_message': 'Have already booked that seat'})
            elif exists_booking and 'reserve' in attrs and attrs['reserve'] \
                    and exists_booking.user.id == attrs['user'].id:
                raise ValidationError({'error_message': 'Have already booked that seat'})

        return attrs

    def update(self, instance, validated_data):
        if validated_data['active'] == 0:
            instance.active = validated_data.get('active', instance.active)

            saved = instance.save()
            if saved:
                reserved_users = Booking.objects.filter(
                    row=instance.row, column=instance.column,
                    seans=instance.seans, reserve=1, send_mail=0
                ).values_list('id', 'user__username')

                if reserved_users.exists():
                    for key, value in reserved_users:
                        Booking.objects.filter(pk=key).update(send_mail=1)
                        django_send_email(
                            'Cinema Booking',
                            'You can booking your reserve seat',
                            'from@example.com',
                            [value],
                            fail_silently=False,
                        )

        elif validated_data['active'] and instance.send_mail:
            instance.active = 1
            instance.reserve = 0
            instance.send_mail = 0
            instance.save()

        return instance

    class Meta:
        model = Booking
        fields = ('row', 'column', 'reserve', 'active', 'seans', 'send_mail')
