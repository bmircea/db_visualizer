from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('db/<int:db_id>/', views.db, name='db'),
]