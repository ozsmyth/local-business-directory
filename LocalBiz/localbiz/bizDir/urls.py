from django.urls import path
from .views import homepage, signupView, loginView, logoutView, businessInfo, ownerDashboard, submitReview, searchView, mapView


urlpatterns = [
    path('home/', homepage, name='hompage'),
    path('business/<slug:slug>/', businessInfo, name='business_detail'),
    path('dashboard/', ownerDashboard, name='owner_dashboard'),
    path('review/<slug:slug>/', submitReview, name='submit_review'),
    path('search/', searchView, name='search'),
    path('map/', mapView, name='map_view'),
    path('signup/', signupView, name='signupage'),
    path('login/', loginView, name='loginpage'),
    path('logout/', logoutView, name='logoutpage'),
]

# http://127.0.0.1:8000/bizDir/home/