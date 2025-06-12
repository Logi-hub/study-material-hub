from django.apps import AppConfig


class StudyMaterialHubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'study_material_hub'
    
def ready(self):
    import study_material_hub.signals
