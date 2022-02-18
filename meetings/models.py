from django.utils import timezone

from django.db import models
from django.conf import settings


class Meeting(models.Model):
    SLOT_CHOICES = (
        (15, 15),
        (30, 30),
        (45, 45),
    )

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    slot_duration_in_minutes = models.PositiveIntegerField(choices=SLOT_CHOICES, default=15)
    reserver_name = models.CharField(max_length=256, blank=True, null=True)
    reserver_email = models.EmailField(blank=True, null=True)

    @property
    def is_reserved(self):
        """
        is meeting already reserved by some other user?
        """
        return self.reserver_name is not None

    @property
    def is_meeting_over(self):
        """
        is meeting over
        """

        return self.end_time < timezone.now()

    def __str__(self):
        return f'{self.title} Duration:{self.slot_duration_in_minutes} minutes, by: {self.created_by.username}'

