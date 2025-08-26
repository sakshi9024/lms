from django.contrib import admin
from .models import Author, Books, UserBook, UserProfile
from .admin_inline_paginator import StackedInlinePaginated  # your custom inline pagination
from django.contrib.auth.models import User, Group
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered


# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = "📚 LMS Admin"
    site_title = "LMS Dashboard"
    index_title = "Welcome to LMS Administration"

    class Media:
        css = {
            'all': ('css/custom_admin.css',),  # ✅ FIXED path
        }


admin_site = CustomAdminSite(name="custom_admin")


# Register default auth models
admin_site.register(User)
admin_site.register(Group)


# Inline with pagination for Books inside Author
class BookInline(StackedInlinePaginated):
    model = Books
    per_page = 5
    pagination_key = 'books'
    template = "admin/edit_inline/stacked_paginated.html"  # keep inside templates/admin/...
    extra = 0
    ordering = ['id']
    fields = ['name', 'author', 'selling_price', 'quantity', 'rent_price', 'category']

    def has_add_permission(self, request, obj=None):
        # Disable adding new inlines to remove the extra empty form
        return False
    


# ✅ Author Admin
@admin.register(Author, site=admin_site)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [BookInline]


# ✅ Books Admin
@admin.register(Books, site=admin_site)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author']


# ✅ UserBook Admin
@admin.register(UserBook, site=admin_site)
class UserBookAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'type']


# ✅ UserProfile Admin
@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'password', 'phone_no', 'address']


# Auto-register all other models (without re-registering these)
for app_config in apps.get_app_configs():
    for model in app_config.get_models():
        try:
            # avoid double registration of models already registered above
            if model not in admin_site._registry:
                admin_site.register(model)
        except AlreadyRegistered:
            pass