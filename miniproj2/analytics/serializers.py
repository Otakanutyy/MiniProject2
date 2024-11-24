from rest_framework import serializers
from analytics.models import ActiveUser

class ActiveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveUser
        fields = ['user', 'api_calls']
