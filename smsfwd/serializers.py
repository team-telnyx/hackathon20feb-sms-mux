from rest_framework import serializers
from . import models


class TeamNumber(serializers.ModelSerializer):
    class Meta:
        model = models.TeamNumber
        fields = ["number", "created", "enabled"]

    # number = serializers.CharField(required=True, max_length=17)
    # created = serializers.DateTimeField(read_only=True)

    # enabled = serializers.BooleanField(default=True)

    # def create(self, validated_data):
    #     return models.TeamNumber.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     instance.number = validated_data.get("number", instance.number)
    #     instance.enabled = validated_data.get("enabled", instance.enabled)
    #     instance.save()
    #     return instance


class TelnyxMessagingProfile(serializers.ModelSerializer):
    class Meta:
        model = models.TelnyxMessagingProfile
        fields = ["profile_id", "updated"]


class Message(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = [
            "id",
            "created",
            "teammate_tn",
            "intermediate_tn",
            "customer_tn",
            "direction",
            "text",
            "delivery_status",
        ]
