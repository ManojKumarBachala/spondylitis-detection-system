from django.urls import include, path

urlpatterns = [
    path("", include("SpondyApp.urls")),
]
