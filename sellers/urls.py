from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.setup_seller_profile, name='setup_seller_profile'),
    path('create-advert/', views.create_advert, name='create_advert'),
    path("my-shop/<int:seller_id>/", views.my_shop, name="my_shop"),
    path("my-adverts/", views.my_adverts, name="my_adverts"),
    path("feedback/", views.feedback, name="feedback"),
    path('performance/<int:seller_id>/', views.performance, name='performance'),
    path("settings/", views.settings, name="settings"),
    path("<int:shop_id>/upload-images/", views.upload_shop_images, name="upload_shop_images"),
    path("edit/<int:pk>/", views.edit_advert, name="edit_advert"),
    path("toggle-status/<int:pk>/", views.toggle_advert_status, name="toggle_advert_status"),
    path("shop/image/<int:image_id>/delete/", views.delete_shop_image, name="delete_shop_image"),
    path("shop/image/<int:image_id>/edit/", views.edit_shop_image, name="edit_shop_image"),
    path("adverts/<int:pk>/delete/", views.delete_advert, name="delete_advert"),
]
