# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Cinema(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name


class Room(models.Model):
    room_name = models.CharField(max_length=50, null=False, blank=False)
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    row_count = models.IntegerField()
    column_count = models.IntegerField()

    def __str__(self):
        return self.cinema.name + ' - ' + self.room_name


class Film(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    duration = models.TimeField(null=False, auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.name


class Seans(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    date = models.DateField(null=False, auto_now=False, auto_now_add=False)
    start_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)
    end_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)


class Booking(models.Model):
    seans = models.ForeignKey(Seans, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    row = models.IntegerField()
    column = models.IntegerField()
    reserve = models.BooleanField(null=True, blank=False)
    active = models.BooleanField(null=True, blank=False)

