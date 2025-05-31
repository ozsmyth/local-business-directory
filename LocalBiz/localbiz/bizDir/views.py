from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from .models import Business, BusinessCategory, BusinessHours, BusinessImage, Review

# Create your views here.

# Homepage View with optional search functionality
# Shows featured and active businesses
def homepage(request):
    return render(request, "user/index.html", {})

# Detailed view of a business with reviews, images and operating hours
def businessInfo(request, slug):
    pass
    return render(request, "user/bizinfo.html", {})

# Business owner dashboard view (requires login)
# Shows all businesses owned by the logged-in user
@login_required
def ownerDashboard(request):
    pass
    return render(request, "user/dashboard.html", {})

# Submit or update a review for a business (requires login)
@login_required
def submitReview(request, slug):
    pass
    return render(request, "user/reviewform.html", {})

# Search view with optional filters for query, city, and category
def searchView(request):
    pass
    return render(request, "user/search_results.html", {})

# Map view of all businesses with coordinates
def mapView(request):
    pass
    return render(request, "user/map.html", {})

# User signup view with form handling
def signupView(request):
    pass
    return render(request, "auth/signup.html", {})

# User login with form validation
def loginView(request):
    pass
    return render(request, "auth/login.html", {})

# Logout view, Ends user session and redirects to homepage
@login_required
def logoutView(request):
    logout(request)
    return redirect("")