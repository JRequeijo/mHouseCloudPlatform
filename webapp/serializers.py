from rest_framework import serializers

from webapp.models import AccountSettings


class AccountSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountSettings
        fields = ("id", "present_history_on_dash", "present_analytics_on_dash")
