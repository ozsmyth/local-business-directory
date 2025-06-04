from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import BusinessForm # You'll create this form
from .models import Business, BusinessCategory, BusinessHours, BusinessImage, Review, UserProfile

# Create your views here.

# Homepage View with optional search functionality
# Shows featured and active businesses
def homepage(request:HttpRequest):
    query = request.GET.get("q")
    businesses = Business.objects.filter(featured=True, is_active=True)
    if query:
        businesses = businesses.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, "user/index.html", {"businesses": businesses})

# Business owner dashboard view (requires login)
# Shows all businesses owned by the logged-in user
@login_required(login_url='/bizDir/login')
def ownerDashboard(request:HttpRequest):
    user = request.user
    businesses = user.owned_businesses.all()

    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = user
            business.save()
            form.save_m2m()  # Save M2M fields like categories
            messages.success(request, "Business added successfully!")
            return redirect("owner_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BusinessForm()
    
    context = {
        "user": user,
        "businesses": businesses,
        "form": form,
    }
    return render(request, "user/dashboard.html", context)

# Detailed view of a business with reviews, images and operating hours
def businessInfo(request:HttpRequest, slug):
    try:
        business = Business.objects.get(slug=slug, is_active=True)
    except Business.DoesNotExist:
        raise Http404("Business not found")
    
    reviews = Review.objects.filter(business=business) # from Review.business
    images = BusinessImage.objects.filter(business=business) # from Review.business
    hours = BusinessHours.objects.filter(business=business) # from Review.business
    context = {
        "business": business,
        "reviews": reviews,
        "images": images,
        "hours": hours
    }
    return render(request, "user/bizinfo.html", context)

@login_required(login_url='/bizDir/login')
def editBusiness(request:HttpRequest, business_id):
    try:
        business = Business.objects.get(id=business_id, owner=request.user)
    except Business.DoesNotExist:
        raise Http404("Business not found.")
    
    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, "Business updated successfully!")
            return redirect("owner_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BusinessForm(instance=business)
    return render(request, "user/edit_business.html", {"form": form, "business": business})

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
def signupView(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role", "regular").strip()

        # Trusting frontend validation (just basic sanity check)
        if password1 != password2:
            return render(request, "auth/signup.html", {"error": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, "auth/signup.html", {"error": "User already exist."})

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            # Assign role to profile (safe approach)
            profile = getattr(user, "profile", None)
            if profile:
                profile.role = role
                profile.save()
            else:
                UserProfile.objects.create(user=user, role=role)
            return redirect("loginpage")

        except Exception as e:
            print(f"Signup Error: {e}")
            return render(request, "auth/signup.html", {"error": "Signup failed. Please try again."})

    return render(request, "auth/signup.html")

# User login with form validation
def loginView(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password")

        if not username or not password:
            return render(request, "auth/login.html", {
                "error": "Both username and password are required.",
                "success": ""
            })
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "auth/login.html", {
                "error": "Invalid username or password.",
                "success": ""
            })
        
        login(request, user)

        # Redirect based on role
        try:
            if user.profile.role == 'owner':
                return redirect("owner_dashboard")
            else:
                return redirect("homepage")  # or some homepage or listing view for regular users
        except UserProfile.DoesNotExist:
            return render(request, "auth/login.html", {
                "error": "User profile not found.",
                "success": ""
            })

    return render(request, "auth/login.html", {"error": "", "success": ""})

# Logout view, Ends user session and redirects to homepage
@login_required(login_url='/bizDir/login')
def logoutView(request):
    logout(request)
    return redirect("homepage")