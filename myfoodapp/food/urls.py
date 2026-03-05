from django.urls import path
from .views import (
    home, cafe, cart_items,  add_to_cart, my_story, submit_feedback, feedback_list
)

urlpatterns = [
    path('', home, name='home'),
    path('cafe/', cafe, name='cafe'),
    path('add-to-cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('my-story/', my_story, name='my_story'),
    path('submit_feedback/', submit_feedback, name='submit_feedback'),
    path('cart/', cart_items, name='cart_items'),
    path('feedback/', feedback_list, name='feedback_list'),
]
