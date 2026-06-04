from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import RegisterSerializer

# Create your views here.

@api_view(['POST'])
def register(request):

    serializer = RegisterSerializer(
        data=request.data
    )

    if serializer.is_valid():
        serializer.save()

        return Response({
            "message": "User registered successfully"
        })

    return Response(
        serializer.errors
    )