from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Property
from .serializers import PropertySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator






from django.core.paginator import Paginator
@api_view(['GET'])
def property_list(request):

    # Query parameters
    title = request.GET.get('title')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    properties = Property.objects.all()

    

    if sort == 'low':
        properties = properties.order_by('price')

    elif sort == 'high':
        properties = properties.order_by('-price')




    if title:
        properties=properties.filter(
            title__icontains=title
        )

    # Search by location
    if location:
        properties = properties.filter(
            location__icontains=location
        )

    # Minimum price
    if min_price:
        properties = properties.filter(
            price__gte=min_price
        )

    # Maximum price
    if max_price:
        properties = properties.filter(
            price__lte=max_price
        )

    # Pagination
    page = request.GET.get('page', 1)

    paginator = Paginator(
        properties,
        5
    )

    properties_page = paginator.get_page(page)

    serializer = PropertySerializer(
        properties_page,
        many=True
    )

    return Response({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": int(page),
        "results": serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_property(request):

    serializer = PropertySerializer(
        data=request.data
    )

    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data)

    return Response(serializer.errors)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_properties(request):

    properties = Property.objects.filter(
        owner=request.user
    )

    serializer = PropertySerializer(
        properties,
        many=True
    )

    return Response(serializer.data)









@api_view(['GET'])
def single_property(request, id):

    property = get_object_or_404(
        Property,
        id=id
    )

    serializer = PropertySerializer(
        property
    )

    return Response(serializer.data)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_property(request, id):

    property = get_object_or_404(
        Property,
        id=id
    )

    if property.owner != request.user:
        return Response(
            {"error": "Permission denied"},
            status=403
        )

    serializer = PropertySerializer(
        property,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property(request, id):

    property = get_object_or_404(
        Property,
        id=id
    )

    if property.owner != request.user:
        return Response(
            {"error": "Permission denied"},
            status=403
        )

    property.delete()

    return Response({
        "message": "Property deleted successfully"
    })


####filter serach


