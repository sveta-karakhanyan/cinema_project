import datetime

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from apps.task.models import Seance


class SeanceForm(ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        duration = cleaned_data.get('film').duration
        room_id = cleaned_data.get('room').id
        date = cleaned_data.get('date')

        start = datetime.timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
        duration = datetime.timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)
        end_time = start + duration

        end_time_obj = datetime.datetime.strptime(end_time.__str__(), '%H:%M:%S').time()
        exists_seance = Seance.objects.filter(start_time__lte=end_time_obj, date=date)

        rooms_list = exists_seance.values_list('room', flat=True)
        if rooms_list:
            if room_id in rooms_list:
                raise ValidationError('Cannot save have already seance in that time')

        if exists_seance.count() == 2:
            raise ValidationError('Cannot be seance in 3 rooms at the same time')

    class Meta:
        model = Seance
        fields = '__all__'
