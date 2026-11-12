from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("predict/", views.predict, name="predict"),
    path("healthz", views.health, name="health"),
]
