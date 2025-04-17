from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job, Application, Category
from .forms import JobForm, JobApplicationForm, JobSearchForm, JobPostForm
from django.shortcuts import render
from .models import Category
from apps.accounts.models import Employer

def companies(request):
    companies = Employer.objects.all()
    return render(request, 'jobs/companies.html', {'companies': companies})
def home(request):
    featured_jobs = Job.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    context = {
        'featured_jobs': featured_jobs,
        'categories': categories,
    }
    return render(request, 'jobs/home.html', context)

def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    
    # Xử lý các filter
    search = request.GET.get('search')
    location = request.GET.get('location')
    job_type = request.GET.get('job_type')
    experience = request.GET.get('experience')
    salary = request.GET.get('salary')

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
        
    if experience:
        jobs = jobs.filter(experience_level=experience)
        
    if salary:
        # Xử lý filter theo salary range
        salary_range = salary.split('-')
        if len(salary_range) == 2:
            min_salary, max_salary = salary_range
            jobs = jobs.filter(
                salary__gte=float(min_salary),
                salary__lte=float(max_salary)
            )
        elif salary.endswith('+'):
            min_salary = float(salary.rstrip('+'))
            jobs = jobs.filter(salary__gte=min_salary)

    # Pagination
    paginator = Paginator(jobs, 9)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'job_types': Job.JOB_TYPE_CHOICES,
        'current_filters': {
            'search': search,
            'location': location,
            'job_type': job_type,
            'experience': experience,
            'salary': salary,
        }
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    application_form = None
    has_applied = False

    if request.user.is_authenticated:
        if request.user.is_job_seeker:
            application_form = JobApplicationForm()
            if hasattr(request.user, 'jobseeker'):
                has_applied = Application.objects.filter(
                    job=job, job_seeker=request.user.jobseeker
                ).exists()

    context = {
        'job': job,
        'application_form': application_form,
        'has_applied': has_applied,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def post_job(request):
    if not hasattr(request.user, 'employer'):
        messages.error(request, "Only employers can post jobs!")
        return redirect('home')
        
    if request.method == 'POST':
        form = JobForm(request.POST)
        print("Received POST data:", request.POST)
        
        if form.is_valid():
            try:
                job = form.save(commit=False)
                job.employer = request.user.employer
                job.save()
                messages.success(request, "Job posted successfully!")
                return redirect('jobs:job_detail', job_id=job.id)
            except Exception as e:
                print("Error saving job:", str(e))
                messages.error(request, f"Error saving job: {str(e)}")
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm()

    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def apply_job(request, job_id):
    if not request.user.is_job_seeker:
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect('jobs:job_detail', job_id=job_id)

    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if Application.objects.filter(job=job, job_seeker=request.user.jobseeker).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('jobs:job_detail', job_id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.job_seeker = request.user.jobseeker
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('dashboard:job_seeker_dashboard')

    return redirect('jobs:job_detail', job_id=job_id)

def search_jobs(request):
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(is_active=True)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if category:
            jobs = jobs.filter(category=category)
        if job_type:
            jobs = jobs.filter(job_type=job_type)

    paginator = Paginator(jobs, 9)  # 9 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'form': form,
    }
    return render(request, 'jobs/search_results.html', context)

def categories(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'jobs/categories.html', context)

def company_detail(request, pk):
    company = get_object_or_404(Employer, pk=pk)
    active_jobs = Job.objects.filter(employer=company, is_active=True)
    
    context = {
        'company': company,
        'active_jobs': active_jobs,
    }
    return render(request, 'jobs/company_detail.html', context)

@login_required
def manage_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Kiểm tra quyền truy cập
    if not request.user.is_employer or request.user.employer != application.job.employer:
        messages.error(request, "You don't have permission to manage this application.")
        return redirect('dashboard:employer_dashboard')  # Sửa từ 'employer' thành 'employer_dashboard'
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['accept', 'reject', 'reviewing']:
            application.status = 'accepted' if action == 'accept' else 'rejected' if action == 'reject' else 'reviewing'
            application.save()
            status_display = application.get_status_display()
            messages.success(request, f"Application status updated to {status_display}")
        else:
            messages.error(request, "Invalid action")
    
    return redirect('dashboard:employer_dashboard')  # Sửa từ 'employer' thành 'employer_dashboard'




