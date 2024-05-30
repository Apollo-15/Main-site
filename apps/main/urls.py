from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('wishlist/', views.WishlistHandler.as_view(), name='wishlist'),
    path('wishlist/add', views.WishlistAddHandler.as_view(), name='wishlist_add'),
    path('wishlist/remove/<int:pk>', views.WishlistDeleteHandler.as_view(), name='wishlist_remove'),
]