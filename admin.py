# jobapp/admin.py
from django.contrib import admin
from .models import UserCustModel, SkillModel, RecuiterModel, JobSeekerModel, JobPostModel, AppliedModel

@admin.register(UserCustModel)
class UserCustModelAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'display_name', 'user_type', 'is_active']
    list_filter = ['user_type', 'is_active']
    search_fields = ['username', 'email', 'display_name']

@admin.register(SkillModel)
class SkillModelAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(RecuiterModel)
class RecuiterModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'phone']
    search_fields = ['company', 'user__username']

@admin.register(JobSeekerModel)
class JobSeekerModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'phone']
    search_fields = ['name', 'user__username']

@admin.register(JobPostModel)
class JobPostModelAdmin(admin.ModelAdmin):
    list_display = ['titel', 'user', 'category', 'number_opening']
    list_filter = ['category']
    search_fields = ['titel', 'user__username']

@admin.register(AppliedModel)
class AppliedModelAdmin(admin.ModelAdmin):
    list_display = ['job_post', 'job', 'status', 'id']
    list_filter = ['status']