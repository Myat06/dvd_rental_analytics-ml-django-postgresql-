from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),  # ← 1. Root URL goes to Dashboard
    path('revenue/', include('case_studies.revenue.urls')), # ← 2. Revenue stays under /revenue/
]