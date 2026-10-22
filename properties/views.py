from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation

from .models import Property
from .serializers import PropertySerializer


@api_view(['GET'])
def property_list(request):

    # --------------------------------
    # Query Parameters
    # --------------------------------

    title = request.GET.get('title')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    # --------------------------------
    # Price Validation
    # --------------------------------

    if min_price:
        try:
            min_price = Decimal(min_price)

        except InvalidOperation:
            return Response({
                "error": "min_price must be a valid number"
            }, status=400)

    if max_price:
        try:
            max_price = Decimal(max_price)

        except InvalidOperation:
            return Response({
                "error": "max_price must be a valid number"
            }, status=400)

    # --------------------------------
    # Price Range Validation
    # --------------------------------

    if min_price is not None and max_price is not None:

        if min_price > max_price:
            return Response({
                "error": "min_price cannot be greater than max_price"
            }, status=400)

    # --------------------------------
    # Properties
    # --------------------------------

    properties = Property.objects.all()

    # --------------------------------
    # Sorting
    # --------------------------------

    if sort == 'low':
        properties = properties.order_by('price')

    elif sort == 'high':
        properties = properties.order_by('-price')

    elif sort:
        return Response({
            "error": "sort must be either 'low' or 'high'"
        }, status=400)

    # --------------------------------
    # Search by Title
    # --------------------------------

    if title:
        properties = properties.filter(
            title__icontains=title
        )

    # --------------------------------
    # Search by Location
    # --------------------------------

    if location:
        properties = properties.filter(
            location__icontains=location
        )

    # --------------------------------
    # Minimum Price
    # --------------------------------

    if min_price is not None:
        properties = properties.filter(
            price__gte=min_price
        )

    # --------------------------------
    # Maximum Price
    # --------------------------------

    if max_price is not None:
        properties = properties.filter(
            price__lte=max_price
        )

    # --------------------------------
    # Pagination
    # --------------------------------

    page = request.GET.get('page', 1)

    try:
        page = int(page)

        if page < 1:
            raise ValueError

    except ValueError:
        return Response({
            "error": "page must be a positive integer"
        }, status=400)

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
        "current_page": page,
        "results": serializer.data
    })


# --------------------------------
# Create Property
# --------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_property(request):

    serializer = PropertySerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save(
            owner=request.user
        )

        return Response(
            serializer.data
        )

    return Response(
        serializer.errors,
        status=400
    )


# --------------------------------
# My Properties
# --------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_properties(request):

    properties = Property.objects.filter(
        owner=request.user
    ).order_by('-id')

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


# --------------------------------
# Single Property
# --------------------------------

@api_view(['GET'])
def single_property(request, id):

    property = get_object_or_404(
        Property,
        id=id
    )

    serializer = PropertySerializer(
        property
    )

    return Response(
        serializer.data
    )


# --------------------------------
# Update Property
# --------------------------------

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_property(request, id):

    property = get_object_or_404(
        Property,
        id=id
    )

    if property.owner != request.user:

        return Response({
            "error": "Permission denied"
        }, status=403)

    serializer = PropertySerializer(
        property,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            serializer.data
        )

    return Response(
        serializer.errors,
        status=400
    )


# --------------------------------
# Delete Property
# --------------------------------

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property(request, id):

    property = get_object_or_404(
        Property,
        id=id
    )

    if property.owner != request.user:

        return Response({
            "error": "Permission denied"
        }, status=403)

    property.delete()

    return Response({
        "message": "Property deleted successfully"
    })