from django.contrib import admin
from django.urls import path, include
from .views import Ocr

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ocr/', Ocr.as_view()),
]