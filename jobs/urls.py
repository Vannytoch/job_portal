from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('job_list', views.job_list, name='job_list'),
    path('post/', views.post_job, name='post_job'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('profile/', views.profile_view, name='profile'),
]
