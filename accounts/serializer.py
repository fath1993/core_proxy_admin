from rest_framework import serializers

from accounts.models import Profile, Panel


class ProfileSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = instance.user.username
        return ret

    class Meta:
        model = Profile
        fields = "__all__"
        depth = 1


