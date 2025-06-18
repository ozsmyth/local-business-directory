from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, Http404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Count, Avg
import calendar
from .forms import BusinessForm, ReviewForm, BusinessImageForm, BusinessHoursForm   # You'll create this form
from .models import Business, BusinessCategory, BusinessHours, BusinessImage, Review, UserProfile

# Create your views here.

# Homepage View with optional search functionality
# Shows featured and active businesses
def homepage(request: HttpRequest):
    query = request.GET.get("q", "")
    category_id = request.GET.get("category")
    # Get featured and active businesses
    businesses = Business.objects.filter(featured=True, is_active=True).select_related("owner").prefetch_related("categories")

    if not businesses.exists():
        # Fallback to active non-featured businesses
        businesses = Business.objects.filter(is_active=True).select_related("owner").prefetch_related("categories")

    if query:
        # Apply search filter regardless of featured status
        businesses = businesses.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_id:
        businesses = businesses.filter(categories__id=category_id)

    # Get all categories and annotate with business count
    categories = BusinessCategory.objects.annotate(
        business_count = Count("businesses", filter=Q(businesses__is_active=True))
    )

    context = {
        "businesses": businesses,
        "query": query,
        "categories": categories,
    }
    return render(request, "user/index.html", context)

# Business owner dashboard view (requires login)
# Shows all businesses owned by the logged-in user
@login_required(login_url='/bizDir/login')
def ownerDashboard(request: HttpRequest):
    user = request.user

    # Permission check: Only Business Owners
    if user.profile.role != 'owner':
        return redirect('homepage')

    # All businesses by this owner
    businesses = user.owned_businesses.all()

    # Summary Stats
    business_count = businesses.count()
    review_count = Review.objects.filter(business__owner=user).count()
    profile_complete = all([user.first_name, user.email, user.profile.role])

    # Handle form submission
    if request.method == "POST":
        business_form = BusinessForm(request.POST, request.FILES)
        image_form = BusinessImageForm(request.POST, request.FILES)
        hours_form = BusinessHoursForm(request.POST)

        # Business Hours: One form per day
        hours_forms = []
        all_hours_valid = True
        for day in range(7):
            form = BusinessHoursForm(request.POST, prefix=f"day_{day}")
            hours_forms.append((calendar.day_name[day], form))
            if not form.is_valid():
                all_hours_valid = False

        if business_form.is_valid() and image_form.is_valid() and all_hours_valid:
            business = form.save(commit=False)
            business.owner = user
            business.save()
            business_form.save_m2m()

            # Save images
            image = image_form.save(commit=False)
            image.business = business
            image.save()

            # Save business hours
            for _, form in hours_forms:
                hour = hours_form.save(commit=False)
                hour.business = business
                hour.save()

            messages.success(request, "Business added successfully!")
            return redirect("owner_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        business_form = BusinessForm()
        image_form = BusinessImageForm()
        hours_forms = [(calendar.day_name[day], BusinessHoursForm(prefix=f"day_{day}")) for day in range(7)]

    context = {
        "user": user,
        "businesses": businesses,
        "business_form": business_form,
        "image_form": image_form,
        "hours_forms": hours_forms,
        "business_count": business_count,
        "review_count": review_count,
        "profile_complete": profile_complete,
    }
    return render(request, "user/dashboard.html", context)

@login_required(login_url='/bizDir/login')
def editBusiness(request:HttpRequest, business_id):
    try:
        if request.user.profile.role != 'owner':
            messages.error(request, "You do not have permission to edit this business.")
            return redirect('homepage')
        
        business = Business.objects.get(id=business_id, owner=request.user)
    except Business.DoesNotExist:
        raise Http404("Business not found.")

    business_form = BusinessForm(request.POST or None, request.FILES or None, instance=business)
    image = BusinessImage.objects.filter(business=business).first()
    image_form = BusinessImageForm(request.POST or None, request.FILES or None, instance=image)

    hours_forms = []
    for day in range(7):
        hours = BusinessHours.objects.filter(business=business, day_of_week=day).first()
        form = BusinessHoursForm(request.POST or None, instance=hours, prefix=f"day_{day}")
        hours_forms.append((calendar.day_name[day], form))

    if request.method == 'POST':
        forms_valid = business_form.is_valid() and image_form.is_valid()
        hours_valid = all(form.is_valid() for _, form in hours_forms)

        if forms_valid and hours_valid:
            business_form.save()
            image_obj = image_form.save(commit=False)
            image_obj.business = business
            image_obj.save()

            for _, form in hours_forms:
                hour_obj = form.save(commit=False)
                hour_obj.business = business
                hour_obj.save()
                
            messages.success(request, "Business updated successfully!")
            return redirect("owner_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, "user/edit_business.html",  {
        "business": business,
        'business_form': business_form,
        'image_form': image_form,
        'hours_forms': hours_forms,
    })

# Detailed view of a business with reviews, images and operating hours
@login_required(login_url='/bizDir/login')
def businessInfo(request:HttpRequest, slug):
    try:
        business = Business.objects.select_related("owner").prefetch_related(
            "categories", "hours", "images", "reviews__user"
        ).get(slug=slug, status='active')
    except Business.DoesNotExist:
        raise Http404("Business not found")
    
    # Increment view count
    business.views += 1
    business.save(update_fields=['views'])

    # Handle review submission
    review_form = None
    user_review_exists = False
    if request.user.is_authenticated:
        user_review_exists = Review.objects.filter(business=business, user=request.user).exists()
        if not user_review_exists:
            if request.method == 'POST':
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    new_review = review_form.save(commit=False)
                    new_review.business = business
                    new_review.user = request.user
                    new_review.save()
                    messages.success(request, "Review submitted successfully!")
                    return redirect('business_detail', slug=slug)
            else:
                review_form = ReviewForm()

    reviews = business.reviews.filter(is_approved=True) # from Review.business
    images = BusinessImage.objects.filter(business=business) # from Review.business
    hours = BusinessHours.objects.filter(business=business).order_by('day_of_week') # from Review.business
    context = {
        "business": business,
        "reviews": reviews,
        "images": images,
        "hours": hours,
        "review_form": review_form,
        "user_review_exists": user_review_exists,
    }
    return render(request, "business/bizinfo.html", context)

def businessList(request:HttpRequest):
    businesses = Business.objects.filter(status='active') \
        .prefetch_related('categories', 'reviews') \
        .annotate(review_count=Count('reviews'), average_rating=Avg('reviews__rating'))

    paginator = Paginator(businesses, 6)  # Show 6 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'business/listing.html', context)

def contact(request):
    return render(request, 'user/contact.html', {})

def about(request):
    return render(request, 'user/about.html', {})

# Search view with optional filters for query, city, and category
def searchView(request: HttpRequest):
    query = request.GET.get("q", "")
    city = request.GET.get("city", "")
    category_id = request.GET.get("category", "")

    businesses = Business.objects.filter(is_active=True).prefetch_related("categories")

    if query:
        businesses = businesses.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    if city:
        businesses = businesses.filter(city__icontains=city)

    selected_category = None
    if category_id.isdigit():
        selected_category = get_object_or_404(BusinessCategory, id=category_id)
        businesses = businesses.filter(categories=selected_category)

    # Add pagination here (e.g., 6 businesses per page)
    paginator = Paginator(businesses.distinct(), 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
        "city": city,
        "selected_category": selected_category,
        "categories": BusinessCategory.objects.all()
    }
    return render(request, "user/search.html", context)

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