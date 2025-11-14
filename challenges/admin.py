from django.contrib import admin
from .models import Category, Challenge, Submission, FirstBlood

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')
    search_fields = ('name',)

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'points', 'is_active', 'get_solve_count')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('team', 'challenge', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'submitted_at', 'challenge__category')
    search_fields = ('team__name', 'challenge__title')
    readonly_fields = ('submitted_at',)

@admin.register(FirstBlood)
class FirstBloodAdmin(admin.ModelAdmin):
    list_display = ('team', 'challenge', 'achieved_at', 'bonus_points')
    list_filter = ('achieved_at',)
    search_fields = ('team__name', 'challenge__title')
    readonly_fields = ('achieved_at',)
