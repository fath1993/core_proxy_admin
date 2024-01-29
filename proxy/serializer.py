from rest_framework import serializers

from proxy.models import Proxy


class ProxySerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['belong_to'] = instance.belong_to.username
        ret['created_at'] = instance.created_at.strftime('%Y-%m-%d - %H:%M')
        ret['updated_at'] = instance.updated_at.strftime('%Y-%m-%d - %H:%M')
        return ret

    class Meta:
        model = Proxy
        fields = "__all__"


