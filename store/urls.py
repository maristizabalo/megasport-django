from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:categoria_slug>', views.store, name='productos_por_categoria'),
    path('category/<slug:categoria_slug>/<slug:producto_slug>', views.detalle_producto, name='detalle_producto'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:producto_id>/', views.submit_review, name='submit_review'),    
]