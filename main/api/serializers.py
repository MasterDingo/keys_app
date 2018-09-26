from rest_framework import serializers

from ..models import Key


class KeySymbolsSerializer(serializers.ModelSerializer):
    ''' Сериалайзер только для самого кода '''
    class Meta:
        model = Key
        fields = ("symbols",)


class KeyDetailsSerializer(serializers.ModelSerializer):
    ''' Сериалайзер для кода и статуса '''
    class Meta:
        model = Key
        fields = ("symbols", "status")
