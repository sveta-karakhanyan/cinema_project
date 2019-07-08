from datetime import datetime
from django.contrib import admin

from apps.task.models import Cinema, Film, Seans, Room


class CinemaAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            for i in range(1, 4):
               Room.objects.create(room_name='Room ' + i, row_count=10, column_count=8, cinema_id=obj.id)


class FilmAdmin(admin.ModelAdmin):
    pass


class SeansAdmin(admin.ModelAdmin):
    list_display = ('film', 'room', 'date', 'start_time', )


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'cinema', 'row_count', 'column_count')
    readonly_fields = ('cinema', 'row_count', 'column_count')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Cinema, CinemaAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Film, FilmAdmin)
admin.site.register(Seans, SeansAdmin)
