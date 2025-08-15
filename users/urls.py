from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view  , name='login'),
    path('logout/', views.logout_view  , name='logout'),
    path('forgot-password/', views.forgot_password_request, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),    
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('verify-registration-otp/', views.verify_registration_otp, name='verify_registration_otp'),
    path('edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('reset-password-profile/', views.reset_password_on_profile, name='reset_password_on_profile'),
]
