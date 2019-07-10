import datetime

from django.contrib import admin

from apps.task.forms import SeansForm
from apps.task.models import Film, Seans, Room


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'row_count', 'column_count')
    readonly_fields = ('row_count', 'column_count')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FilmAdmin(admin.ModelAdmin):
    pass


class SeansAdmin(admin.ModelAdmin):
    form = SeansForm
    list_display = ('film', 'room', 'date', 'start_time', 'end_time')
    readonly_fields = ('end_time', )

    def save_model(self, request, obj, form, change):
        start_time = obj.start_time
        duration = obj.film.duration

        start = datetime.timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
        duration = datetime.timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)
        end_time = start + duration

        obj.end_time = datetime.datetime.strptime(end_time.__str__(), '%H:%M:%S').time()
        super().save_model(request, obj, form, change)


admin.site.register(Room, RoomAdmin)
admin.site.register(Film, FilmAdmin)
admin.site.register(Seans, SeansAdmin)
