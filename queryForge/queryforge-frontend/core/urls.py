from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('crypto/', views.crypto_view, name='crypto'),
    path('stocks/', views.stocks_view, name='stocks'),
    path('health/', views.health_check, name='health_check'),
    
    # API proxy endpoints
    re_path(r'^proxy/crypto/(?P<path>.*)$', views.api_proxy_crypto, name='proxy_crypto'),
    re_path(r'^proxy/stock/(?P<path>.*)$', views.api_proxy_stock, name='proxy_stock'),
    path('proxy/queries/', views.api_proxy_queries, name='proxy_queries'),
    re_path(r'^api/crypto/(?P<path>.*)$', views.api_proxy_crypto, name='api_crypto'),
    re_path(r'^api/stock/(?P<path>.*)$', views.api_proxy_stock, name='api_stock'),
]