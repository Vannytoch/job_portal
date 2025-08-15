from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
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

@login_required
def add_job(request):
    if request.method == "POST":
        job = Job(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            company=request.POST.get('company'),
            location=request.POST.get('location'),
            posted_by=request.user,
            is_active='is_active' in request.POST,
            salary_min=float(request.POST.get('salary_min') or 0),
            salary_max=float(request.POST.get('salary_max') or 0),
        )
        job.save()
        # Optionally add messages.success here
        return redirect('profile')  # Or wherever you want

    return redirect('profile')

def contact_view(request):
    return render(request, 'jobs/contact.html')

def search_jobs(request):
    query = request.GET.get('q', '')
    if query:
        jobs = Job.objects.filter(title__icontains=query, is_active=True)
        results = list(jobs.values('id', 'title'))
    else:
        results = []
    return JsonResponse(results, safe=False)


def custom_404(request, exception):
    return render(request, 'jobs/404.html', status=404)
