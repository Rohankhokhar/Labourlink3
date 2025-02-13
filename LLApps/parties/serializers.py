from rest_framework import serializers
from LLApps.parties.models import PartiesDetail

class PartyDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = PartiesDetail
        fields = "__all__"

    def create(self, validated_data):
        # 🚨 Remove manual ido assignment, let Django handle it
        return super().create(validated_data)


