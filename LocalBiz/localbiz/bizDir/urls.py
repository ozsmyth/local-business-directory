from django.urls import path
from .views import homepage, signupView, loginView, logoutView, businessInfo, ownerDashboard, searchView, editBusiness, businessList, contact, about


urlpatterns = [
    path('home/', homepage, name='homepage'),
    path('business/<slug:slug>/', businessInfo, name='business_detail'),
    path('dashboard/', ownerDashboard, name='owner_dashboard'),
    path("business/edit/<int:business_id>/", editBusiness, name="edit_business"),
    path('listings/', businessList, name='business_list'),
    path('search/', searchView, name='search'),
    path('about/', about, name='about'),
    # path('services/', services, name='services'),
    path('contact/', contact, name='contact'),
    # path('terms/', terms, name='terms'),
    # path('privacy/', privacy, name='privacy'),
    path('signup/', signupView, name='signupage'),
    path('login/', loginView, name='loginpage'),
    path('logout/', logoutView, name='logoutpage'),
]

# http://127.0.0.1:8000/bizDir/home/