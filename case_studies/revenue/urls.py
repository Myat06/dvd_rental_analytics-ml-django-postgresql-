from django.urls import path
from . import views

app_name = 'revenue'

urlpatterns = [
    path('', views.revenue_overview, name='overview'),
]