from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('', views.customer_overview, name='overview'),
]