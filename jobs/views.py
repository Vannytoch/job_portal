from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Job
from .forms import JobForm, ApplicationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

@login_required
def post_job(request):
    if request.user.role != 'recruiter':
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('home')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})

def home(request):
    if request.user.is_authenticated:
        print(request.user)
    jobs = Job.objects.filter(is_active=True)
    return render(request, 'jobs/home.html', {'jobs': jobs})

def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    paginator = Paginator(jobs, 6)  # 6 jobs per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'jobs/job_list.html', {'jobs': page_obj})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, f'You have successfully applied for "{job.title}".')
            return redirect('job_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ApplicationForm()

    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})

def profile_view(request):
    return render(request, 'users/profile.html')