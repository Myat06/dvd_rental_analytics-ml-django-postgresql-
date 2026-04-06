from django.apps import AppConfig

class CustomerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'case_studies.customer'
    label = 'customer'  # Short name for migrations & queries
