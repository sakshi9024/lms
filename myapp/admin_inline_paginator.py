from django.contrib.admin.options import StackedInline
from django.core.paginator import Paginator
from django.utils.functional import cached_property


class StackedInlinePaginated(StackedInline):
    per_page = 2
    pagination_key = None  # e.g. "books"

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)

        # Capture inline-level configuration for use inside nested class methods
        pagination_key = self.pagination_key or (self.model._meta.model_name if hasattr(self, 'model') else 'page')
        per_page = getattr(self, 'per_page', 5)
        ordering = list(getattr(self, 'ordering', ['id']))

        class PaginatedFormSet(FormSet):
            @cached_property
            def base_queryset(self):
                # Base queryset that Django admin inline formset would use
                qs = super(PaginatedFormSet, self).get_queryset()
                # Ensure deterministic ordering before pagination
                return qs.order_by(*ordering)

            @cached_property
            def paginator(self):
                return Paginator(self.base_queryset, per_page)

            @cached_property
            def page_obj(self):
                page_num = request.GET.get(f"{pagination_key}_page", 1)
                return self.paginator.get_page(page_num)

            def get_queryset(self):
                # Only return the objects for the current page
                return self.page_obj.object_list

            def initial_form_count(self):
                # Number of forms should match the number of objects on this page
                return len(self.get_queryset())

            def total_form_count(self):
                # We are not allowing extras here; keep equal to current page size
                return self.initial_form_count()

        # Expose these for the template (e.g., stacked_paginated.html)
        setattr(PaginatedFormSet, 'pagination_key', pagination_key)
        setattr(PaginatedFormSet, 'per_page', per_page)

        return PaginatedFormSet

