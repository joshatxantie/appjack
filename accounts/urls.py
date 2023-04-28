from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = "accounts"

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit/', views.edit_profile, name='edit'),
    path('users/', views.view_all_users, name='users'),
    path('edit/<int:user_id>', views.edit_profile_admin, name="edit_user"),
    # other app urls
]