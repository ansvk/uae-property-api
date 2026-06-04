from django.urls import path
from .views import *
urlpatterns = [
     path('properties/', property_list),

    path(
        'properties/create/',
        create_property
    ),

    path(
        'properties/<int:id>/',
        single_property
    ),

    path(
        'properties/<int:id>/update/',
        update_property
    ),

    path(
        'properties/<int:id>/delete/',
        delete_property
    ),

    path(
        'my-properties/',
        my_properties
    ),
]
