from rest_framework.mixins import DestroyModelMixin

from django.core.mail import send_mail as django_send_email

from apps.task.models import Reserve


class UnbookedDestroyModelMixin(DestroyModelMixin):
    def perform_destroy(self, instance):
        booking, deleted = instance.delete()

        if deleted:
            reserved_users = Reserve.objects.filter(
                row=instance.row, column=instance.column, seance=instance.seance
            ).values_list('id', 'user__email')

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
