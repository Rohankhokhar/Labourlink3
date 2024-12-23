from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from LLApps.parties.models import PartiesDetail
from LLApps.parties.serializers import PartyDetailSerializers

@api_view(['GET', 'POST'])
def PartiesListAPI(request):
    if request.method == 'GET':
        labour_id = request.query_params.get('labour')  # Get the labour ID from query parameters
        if labour_id:
            querySet = PartiesDetail.objects.filter(labour_id=labour_id)  # Filter by labour ID
        else:
            querySet = PartiesDetail.objects.all()  # Return all entries if no filter is applied
        
        serializer = PartyDetailSerializers(querySet, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        serializer = PartyDetailSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def PartiesDetailAPI(request, party_id):
    try:
        querySet = PartiesDetail.objects.get(pk=party_id)
    except PartiesDetail.DoesNotExist:
        return Response({'message': f"Party details not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PartyDetailSerializers(querySet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        serializer = PartyDetailSerializers(querySet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        serializer = PartyDetailSerializers(querySet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        querySet.delete()
        return Response({'message': 'Party details deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

