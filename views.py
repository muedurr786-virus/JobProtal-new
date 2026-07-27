# jobapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    View, TemplateView, CreateView, UpdateView, 
    ListView, DetailView, FormView
)
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q

from .models import (
    UserCustModel, SkillModel, RecuiterModel, 
    JobSeekerModel, JobPostModel, AppliedModel
)
from .forms import (
    UserCustForm, AuthForm, SkillForm, 
    RecuiterForm, JobSeekerForm, JobpostForm
)


# ============== Mixins ==============

class RecruiterRequiredMixin(UserPassesTestMixin):
    """Only allow recruiters to access the view"""
    def test_func(self):
        return self.request.user.user_type == 'Recuiter'


class JobSeekerRequiredMixin(UserPassesTestMixin):
    """Only allow job seekers to access the view"""
    def test_func(self):
        return self.request.user.user_type == 'JobSeeker'


class ProfileRequiredMixin(LoginRequiredMixin):
    """Ensure user has completed their profile"""
    def dispatch(self, request, *args, **kwargs):
        if not self.check_profile_exists():
            messages.warning(request, 'Please complete your profile first!')
            if request.user.user_type == 'Recuiter':
                return redirect('jobapp:recruiter_profile')
            else:
                return redirect('jobapp:jobseeker_profile')
        return super().dispatch(request, *args, **kwargs)
    
    def check_profile_exists(self):
        user = self.request.user
        if user.user_type == 'Recuiter':
            return hasattr(user, 'recuitermodel')
        elif user.user_type == 'JobSeeker':
            return hasattr(user, 'jobseekermodel')
        return False


# ============== Home View ==============

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_jobs'] = JobPostModel.objects.count()
        context['total_seekers'] = JobSeekerModel.objects.count()
        context['total_recruiters'] = RecuiterModel.objects.count()
        context['recent_jobs'] = JobPostModel.objects.select_related('user').order_by('-id')[:6]
        context['skills'] = SkillModel.objects.all()
        return context


# ============== Authentication Views ==============

class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = UserCustForm
    success_url = reverse_lazy('jobapp:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please correct the errors.')
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = AuthForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.user_type == 'Recuiter':
            if hasattr(user, 'recuitermodel'):
                return reverse('jobapp:my_posts')
            return reverse('jobapp:recruiter_profile')
        else:
            if hasattr(user, 'jobseekermodel'):
                return reverse('jobapp:job_list')
            return reverse('jobapp:jobseeker_profile')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid credentials. Please try again.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('jobapp:home')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


# ============== Profile Views ==============

class RecruiterProfileView(LoginRequiredMixin, RecruiterRequiredMixin, UpdateView):
    template_name = 'recruiter/profile.html'
    form_class = RecuiterForm
    success_url = reverse_lazy('jobapp:my_posts')
    
    def get_object(self, queryset=None):
        profile, created = RecuiterModel.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_exists'] = hasattr(self.request.user, 'recuitermodel')
        return context


class JobSeekerProfileView(LoginRequiredMixin, JobSeekerRequiredMixin, UpdateView):
    template_name = 'jobseeker/profile.html'
    form_class = JobSeekerForm
    success_url = reverse_lazy('jobapp:job_list')
    
    def get_object(self, queryset=None):
        profile, created = JobSeekerModel.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_exists'] = hasattr(self.request.user, 'jobseekermodel')
        return context


# ============== Job Views ==============

class JobListView(ListView):
    template_name = 'jobseeker/job_list.html'
    model = JobPostModel
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = JobPostModel.objects.select_related('user', 'user__recuitermodel').prefetch_related('skill_set')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(titel__icontains=search) |
                Q(user__recuitermodel__company__icontains=search) |
                Q(skill_set__name__icontains=search)
            ).distinct()
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Skill filter
        skill = self.request.GET.get('skill')
        if skill:
            queryset = queryset.filter(skill_set__id=skill).distinct()
        
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = SkillModel.objects.all()
        context['categories'] = JobPostModel.Category
        context['search'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_skill'] = self.request.GET.get('skill', '')
        return context


class JobDetailView(DetailView):
    template_name = 'jobseeker/job_detail.html'
    model = JobPostModel
    context_object_name = 'job'
    
    def get_queryset(self):
        return JobPostModel.objects.select_related('user', 'user__recuitermodel').prefetch_related('skill_set')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.user_type == 'JobSeeker':
            context['already_applied'] = AppliedModel.objects.filter(
                job_post=self.request.user.jobseekermodel,
                job=self.object
            ).exists()
        else:
            context['already_applied'] = False
        return context


class JobApplyView(LoginRequiredMixin, JobSeekerRequiredMixin, View):
    def post(self, request, pk):
        job = get_object_or_404(JobPostModel, pk=pk)
        job_seeker = get_object_or_404(JobSeekerModel, user=request.user)
        
        # Check if already applied
        if AppliedModel.objects.filter(job_post=job_seeker, job=job).exists():
            messages.warning(request, 'You have already applied for this job!')
            return redirect('jobapp:job_detail', pk=pk)
        
        # Check if profile is complete
        if not job_seeker.resume:
            messages.error(request, 'Please upload your resume first!')
            return redirect('jobapp:jobseeker_profile')
        
        # Create application
        AppliedModel.objects.create(
            job_post=job_seeker,
            job=job,
            status='Pending'
        )
        
        messages.success(request, 'Application submitted successfully!')
        return redirect('jobapp:my_applications')


# ============== Recruiter Job Management ==============

class JobPostCreateView(LoginRequiredMixin, RecruiterRequiredMixin, CreateView):
    template_name = 'recruiter/post_job.html'
    form_class = JobpostForm
    success_url = reverse_lazy('jobapp:my_posts')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Job posted successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = SkillModel.objects.all()
        return context


class MyPostsView(LoginRequiredMixin, RecruiterRequiredMixin, ListView):
    template_name = 'recruiter/my_posts.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        return JobPostModel.objects.filter(
            user=self.request.user
        ).prefetch_related('skill_set').order_by('-id')


class JobApplicationsView(LoginRequiredMixin, RecruiterRequiredMixin, DetailView):
    template_name = 'recruiter/applications.html'
    model = JobPostModel
    context_object_name = 'job'
    
    def get_queryset(self):
        return JobPostModel.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = AppliedModel.objects.filter(
            job=self.object
        ).select_related('job_post', 'job_post__user').order_by('-id')
        context['status_choices'] = AppliedModel.Status
        return context


class UpdateApplicationStatusView(LoginRequiredMixin, RecruiterRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(AppliedModel, pk=pk)
        new_status = request.POST.get('status')
        
        # Verify the job belongs to the current recruiter
        if application.job.user != request.user:
            messages.error(request, 'Permission denied!')
            return redirect('jobapp:my_posts')
        
        if new_status in dict(AppliedModel.Status).keys():
            application.status = new_status
            application.save()
            messages.success(request, f'Application status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status!')
        
        return redirect('jobapp:job_applications', pk=application.job.pk)


# ============== Job Seeker Views ==============

class MyApplicationsView(LoginRequiredMixin, JobSeekerRequiredMixin, ListView):
    template_name = 'jobseeker/my_applications.html'
    context_object_name = 'applications'
    paginate_by = 10
    
    def get_queryset(self):
        job_seeker = get_object_or_404(JobSeekerModel, user=self.request.user)
        return AppliedModel.objects.filter(
            job_post=job_seeker
        ).select_related('job', 'job__user', 'job__user__recuitermodel').order_by('-id')


# ============== Skill Management ==============

class SkillCreateView(LoginRequiredMixin, CreateView):
    template_name = 'skill/add.html'
    model = SkillModel
    form_class = SkillForm
    success_url = reverse_lazy('jobapp:add_skill')
    
    def form_valid(self, form):
        messages.success(self.request, f'Skill "{form.instance.name}" added successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = SkillModel.objects.all().order_by('name')
        return context