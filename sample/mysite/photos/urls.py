from django.urls import path
from .views import PhotoListView, PhotoCreateView

urlpatterns = [
    path('', PhotoListView.as_view(), name='index'),
    path('create', PhotoCreateView.as_view(), name='form'),
]
