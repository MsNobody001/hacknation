from django.urls import path
from . import views

urlpatterns = [
    path('sample/', views.SampleView.as_view(), name="sample")
]