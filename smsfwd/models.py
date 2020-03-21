import logging

from django.conf import settings
from django.db import models
from django.urls import reverse
import telnyx

L = logging.getLogger(__name__)


class TelnyxMessagingProfile(models.Model):
    profile_id = models.CharField(max_length=40, null=False, blank=True)
    updated = models.DateTimeField(auto_now=True)

    ## SINGLETON MODE
    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        self.pk = 1
        super().save(*args, **kwargs)

        if self.profile_id:
            # update profile settings (fixme...this is kinda dirty.)
            L.info("Updating webhook/version on Telnyx messaging profile")
            msg_prof = telnyx.MessagingProfile(id=self.profile_id)
            msg_prof.refresh()
            msg_prof.webhook_api_version = "2"
            msg_prof.webhook_url = settings.WEBHOOK_BASE_URL + reverse(
                "smsfwd:telnyx_webhook"
            )
            msg_prof.save()
            L.debug(
                "Updated profile %s at %s, webhook: %s",
                msg_prof.id,
                msg_prof.updated_at,
                msg_prof.webhook_url,
            )

    def delete(self, *args, **kwargs):  # pylint: disable=arguments-differ
        pass

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


# class TelnyxMessagingPhoneNumber(models.Model):
#     id = models.CharField(primary_key=True, max_length=40)
#     created = models.DateTimeField(auto_now_add=True)

#     number = models.CharField(max_length=17, db_index=True)
#     # profile = models.ForeignKey(TelnyxMessagingProfile, null=True)

#     class Meta:
#         ordering = ["created"]


class TeamNumber(models.Model):
    number = models.CharField(primary_key=True, max_length=17)
    created = models.DateTimeField(auto_now_add=True)

    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]


class CustomerNumber(models.Model):
    number = models.CharField(primary_key=True, max_length=17)
    created = models.DateTimeField(auto_now_add=True)

    mux_prefix = models.CharField(db_index=True, max_length=10, unique=True)
    teammate = models.ForeignKey(to=TeamNumber, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["created"]


class Message(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField(auto_now_add=True)

    teammate = models.ForeignKey(to=TeamNumber, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(
        to=CustomerNumber, null=True, on_delete=models.SET_NULL
    )
    intermediate_tn = models.CharField(max_length=17)  # Telnyx TN

    DIR_IN = "in"
    DIR_OUT = "out"
    DIR_CHOICES = [
        (DIR_IN, "Inbound (Customer to Team)"),
        (DIR_OUT, "Outbound (Team to Customer)"),
    ]

    direction = models.CharField(max_length=4, choices=DIR_CHOICES)

    # denormalized locally to survive deleting records
    teammate_tn = models.CharField(max_length=17)
    customer_tn = models.CharField(max_length=17)
    # denormalized remotely to avoid network delay
    text = models.TextField()
    delivery_status = models.CharField(max_length=20)

    class Meta:
        ordering = ["created"]
