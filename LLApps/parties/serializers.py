from rest_framework import serializers
from LLApps.parties.models import PartiesDetail

class PartyDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = PartiesDetail
        fields = "__all__"