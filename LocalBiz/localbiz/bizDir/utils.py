from django.contrib.auth.models import User
from .models import UserProfile

# Safe access to profile
def get_user_profile(user: User) -> UserProfile | None:
    try:
        return user.profile
    except (UserProfile.DoesNotExist, AttributeError):
        return None

def is_business_owner(user: User) -> bool:
    profile = get_user_profile(user)
    return user.is_authenticated and profile and profile.role == 'owner'

def is_regular_user(user: User) -> bool:
    profile = get_user_profile(user)
    return user.is_authenticated and profile and profile.role == 'regular'

def get_user_role(user: User) -> str:
    profile = get_user_profile(user)
    return profile.role if profile else 'unknown'
