from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# Create your models here.

class BusinessCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)  # For frontend display
    
    def __str__(self):
        return self.name

class Business(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True) # Added this part
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_businesses')
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    categories = models.ManyToManyField(BusinessCategory, related_name='businesses')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    promoted_until = models.DateField(null=True, blank=True) # Added this part
    established_date = models.DateField(null=True, blank=True)
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True) # Added this part
    views = models.PositiveBigIntegerField(default=0) # Added this part
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs): # Added this part
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True) # changed this part
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count() # changed this part
        return 0

class BusinessHours(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='hours')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    closed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('business', 'day_of_week')
    
    def __str__(self):
        if self.closed:
            return f"{self.get_day_of_week_display()}: Closed"
        return f"{self.get_day_of_week_display()}: {self.opening_time} - {self.closing_time}"

class BusinessImage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='business_images/')
    caption = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Image for {self.business.name}"

class Review(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True) # Added this part
    updated_date = models.DateTimeField(auto_now=True) # Added this part
    is_approved = models.BooleanField(default=True) # Added this part
    
    class Meta:
        unique_together = ('business', 'user')
    
    def __str__(self):
        return f"Review for {self.business.name} by {self.user.username}"