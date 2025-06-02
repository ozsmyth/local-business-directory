from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from django.db import IntegrityError #import integrity error for handling unique constraint
from .forms import BusinessForm # You'll create this form
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
    try:
        business = Business.objects.filter(slug=slug, is_active=True).first()
    except Business.DoesNotExist:
        raise IntegrityError("Business not found")
    
    reviews = business.reviews.all() # from Review.business
    images = business.images.all() # from Review.business
    hours = business.hours.all() # from Review.business
    context = {
        "business": business,
        "reviews": reviews,
        "images": images,
        "hours": hours
    }
    return render(request, "user/bizinfo.html", context)


# Business owner dashboard view (requires login)
# Shows all businesses owned by the logged-in user
@login_required(login_url='/bizDir/login')
def ownerDashboard(request:HttpRequest):
    user = request.user
    businesses = user.owned_businesses.all()
    form = BusinessForm()

    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = user
            business.save()
            form.save_m2m()  # Save M2M fields like categories
            return redirect("owner_dashboard")

    return render(request, "user/dashboard.html", {
        "user": user,
        "businesses": businesses,
        "form": form,
    })


# Submit or update a review for a business (requires login)
@login_required(login_url='/bizDir/login')
def submitReview(request:HttpRequest, slug):
    business = Business.objects.get(slug=slug, is_active=True)
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
    return render(request, "user/map.html", {"businesses": businesses})


# User signup view with form handling
def signupView(request:HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        # password2 = request.POST.get("password2")
        try:
            user_exist = User.objects.filter(username=username).first()
            if user_exist:
                return render(request, "auth/signup.html", {"error":"User already exist.", "success":None})
            # Getting here means we are good to signup a user
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            print(user)
            # make a user a business owner
            Owner = Business.objects.create(owner=user, email=email)
            Owner.save()
            return redirect("loginpage")
        except:
            return render(request, "auth/signup.html", {"error":"Invalid Credentials.", "success":None})
    return render(request, "auth/signup.html", {"error": None, "success":None})

# User login with form validation
def loginView(request:HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        #validate inputs
        if not username or not password:
            return render(request, "auth/login.html", {"error":"Both username and password are required.", "success":""})
        try:
            user = authenticate(username=username, password=password)
            if user == None:
                return render(request, "auth/login.html", {"error":"Not a valid user."})
            login(request, user)
            return redirect('/bizDir/dashboard/') 
        except:
            return render(request, "auth/login.html", {"error":"Error Occurred.... Username or email required."})
    return render(request, "auth/login.html", {"error": "", "success": ""})

# @login_required(login_url='/bizDir/login')
# def addBusiness(request:HttpRequest):
#     if request.method == "POST":
#         form = BusinessForm(request.POST, request.FILES)
#         if form.is_valid():
#             business = form.save(commit=False)
#             business.owner = request.user
#             business.save()
#             form.save_m2m() # For ManyToMany relationships
#             return redirect("owner_dashboard")
#     else:
#         form = BusinessForm()
#     return render(request, "user/add_business.html", {"form": form})


@login_required(login_url='/bizDir/login')
def editBusiness(request:HttpRequest, business_id):
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            return redirect("owner_dashboard")
    else:
        form = BusinessForm(instance=business)
    return render(request, "user/edit_business.html", {"form": form, "business": business})


# Logout view, Ends user session and redirects to homepage
@login_required(login_url='/bizDir/login')
def logoutView(request):
    logout(request)
    return redirect("homepage")