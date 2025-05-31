from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from .models import Business, BusinessCategory, BusinessHours, BusinessImage, Review

# Create your views here.

# Homepage View with optional search functionality
# Shows featured and active businesses
def homepage(request:HttpRequest):
    query = request.GET.get("q")
    businesses = Business.objects.filter(featured=True, is_active=True)
    if query:
        businesses = businesses.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, "user/index.html", {"businesses": businesses})

# Detailed view of a business with reviews, images and operating hours
def businessInfo(request:HttpRequest, slug):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    reviews = business.reviews.filter()
    images = business.images.all()
    hours = business.hours.all()
    context = {
        "business": business,
        "reviews": reviews,
        "images": images,
        "hours": hours
    }
    return render(request, "user/bizinfo.html", context)

# Business owner dashboard view (requires login)
# Shows all businesses owned by the logged-in user
@login_required
def ownerDashboard(request:HttpRequest):
    businesses = request.user.owned_businesses.all()
    return render(request, "user/dashboard.html", {"businesses": businesses})

# Submit or update a review for a business (requires login)
@login_required
def submitReview(request:HttpRequest, slug):
    business = get_object_or_404(Business, slug=slug, is_active=True)
    if request.method == "POST":
        try:
            rating = int(request.POST.get("rating"))
            comment = request.POST.get("comment")
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5")
            # Create or update the review
            Review.objects.update_or_create(
                business=business,
                user=request.user,
                defaults={"rating": rating, "comment": comment}
            )
            return redirect("business_detail", slug=slug)
        except Exception as e:
            # Return form with error
            return render(request, "user/reviewform.html", {
                "business": business,
                "error": str(e)
            })
    # GET request shows empty form
    return render(request, "user/reviewform.html", {"business": business})

# Search view with optional filters for query, city, and category
def searchView(request:HttpRequest):
    query = request.GET.get("q")
    city = request.GET.get("city")
    category = request.GET.get("category")

    businesses = Business.objects.filter(is_active=True)

    if query:
        businesses = businesses.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if city:
        businesses = businesses.filter(city__icontains=city)
    if category:
        businesses = businesses.filter(categories__name__icontains=category)
    return render(request, "user/search.html", {"businesses": businesses.distinct()})

# Map view of all businesses with coordinates
def mapView(request):
    businesses = Business.objects.filter(latitude__isnull=False, longitude__isnull=False, is_active=True)
    return render(request, "directory/map.html", {"businesses": businesses})

# User signup view with form handling
def signupView(request:HttpRequest):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "auth/signup.html", {"form": form})

# User login with form validation
def loginView(request:HttpRequest):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "auth/login.html", {"form": form})

# Logout view, Ends user session and redirects to homepage
@login_required
def logoutView(request):
    logout(request)
    return redirect("homepage")