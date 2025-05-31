from django.urls import path
from .views import homepage, signupView, loginView, logoutView


urlpatterns = [
    path('home/', homepage, name='bizdir-hompage'),
    path('signup/', signupView, name='bizDir-signup'),
    path('login/', loginView, name='bizDir-login'),
    path('logout/', logoutView, name='bizDir-logout'),
]

# http://127.0.0.1:8000/bizDir/home/