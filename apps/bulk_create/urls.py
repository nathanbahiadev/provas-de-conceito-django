from django.urls import path

from apps.bulk_create import views


app_name = 'bulk_create'

urlpatterns = [
    path('receive/<int:qtde>', views.receber_json_processos_temporarios),
    path('worker/<int:qtde>/<int:limit>', views.worker),
]
