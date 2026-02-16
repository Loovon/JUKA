from django.urls import path
from . import views

urlpatterns = [
    path('cart/add/<int:advert_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path("update/", views.update_cart, name="update_cart"),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('saved-items/', views.saved_items, name='saved_items'),
    path('save-item/<int:advert_id>/', views.save_item, name='save_item'),
    path("add-review/<int:advert_id>/", views.add_review, name="add_review"),
]
