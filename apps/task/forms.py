import datetime

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from apps.task.models import Seans


class SeansForm(ModelForm):

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
        exists_seans = Seans.objects.filter(end_time__gte=start_time, start_time__lte=end_time_obj, date=date)

        rooms_list = exists_seans.values_list('room', flat=True)
        if rooms_list:
            if room_id in rooms_list:
                raise ValidationError('Cannot save have already seans in that time')

        if exists_seans.count() == 2:
            raise ValidationError('Cannot be seans in 3 rooms at the same time')

    class Meta:
        model = Seans
        fields = '__all__'
