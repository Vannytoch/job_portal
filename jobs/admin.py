from django.contrib import admin
from .models import Job, Application

# Register your models here.
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'posted_by', 'posted_at', 'is_active')
    list_filter = ('is_active', 'posted_at', 'location', 'company')
    search_fields = ('title', 'company', 'location', 'description')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'applied_at')
    list_filter = ('applied_at',)
    search_fields = ('job__title', 'applicant__username')