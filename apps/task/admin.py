from django.contrib import admin

from apps.task.forms import SeanceForm
from apps.task.models import Film, Seance, Room, Seat


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SeatAdmin(admin.ModelAdmin):
    list_display = ('row', 'column', 'room')
    readonly_fields = ('row', 'column', 'room')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class FilmAdmin(admin.ModelAdmin):
    pass


class SeanceAdmin(admin.ModelAdmin):
    form = SeanceForm
    list_display = ('film', 'room', 'date', 'start_time', )


admin.site.register(Room, RoomAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Film, FilmAdmin)
admin.site.register(Seance, SeanceAdmin)
