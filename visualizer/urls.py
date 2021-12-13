from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('db/<str:db_name>/', views.db, name='db'),
    path('db/query', views.query, name='query')
]