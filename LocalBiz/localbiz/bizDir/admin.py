from django.contrib import admin
from .models import BusinessCategory, Business, BusinessHours, BusinessImage, Review, UserProfile

# Register your models here.
admin.site.register(BusinessCategory)
admin.site.register(Business)
admin.site.register(BusinessHours)
admin.site.register(BusinessImage)
admin.site.register(Review)
admin.site.register(UserProfile)