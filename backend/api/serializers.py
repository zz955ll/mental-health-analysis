from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)

class SendCodeSerializer(serializers.Serializer):
    to_mail = serializers.EmailField()