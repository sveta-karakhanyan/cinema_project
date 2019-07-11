from django.contrib import admin

from apps.task.forms import SeanceForm
from apps.task.models import Film, Seance, Room


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'row_count', 'column_count')
    readonly_fields = ('row_count', 'column_count')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FilmAdmin(admin.ModelAdmin):
    pass


class SeanceAdmin(admin.ModelAdmin):
    form = SeanceForm
    list_display = ('film', 'room', 'date', 'start_time', )


admin.site.register(Room, RoomAdmin)
admin.site.register(Film, FilmAdmin)
admin.site.register(Seance, SeanceAdmin)
