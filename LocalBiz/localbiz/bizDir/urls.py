from django.urls import path
from .views import homepage


urlpatterns = [
    path('home/', homepage, name='bizdir-hompage'),
]

# http://127.0.0.1:8000/bizDir/home/