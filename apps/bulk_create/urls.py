from django.urls import path

from apps.bulk_create import views


app_name = 'bulk_create'

urlpatterns = [
    path('receive/<int:qtde_processos>', views.receber_json_processos_temporarios),
    path('worker/<int:qtde_workers>/<int:limite_processos>', views.worker),
]
