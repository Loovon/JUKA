from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('products/category/<slug:category_slug>/', views.product_list_by_category, name='product_list_by_category'),
    path('products/<int:advert_id>/', views.product_detail, name='product_detail'),
    path("save/<int:advert_id>/", views.save_advert, name="save_advert"),
    path("saved/", views.saved_list, name="saved_list"),
    path('', views.product_list, name='product_list'),
    path("offer/<int:offer_id>/", views.offer_detail, name="offer_detail"),
    path("review/edit/<int:review_id>/", views.edit_review, name="edit_review"),
    path("review/delete/<int:review_id>/", views.delete_review, name="delete_review"),
]
