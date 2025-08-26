from django.contrib.admin.options import StackedInline
from django.core.paginator import Paginator
from django.utils.functional import cached_property


class StackedInlinePaginated(StackedInline):
    per_page = 2
    pagination_key = None  # e.g. "books"

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)

        class PaginatedFormSet(FormSet):
            pagination_key = self.pagination_key
            per_page = self.per_page
            ordering = getattr(self, 'ordering', ['id'])

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Ensure no blank form is appended
                self.extra = 0

            @cached_property
            def base_queryset(self):
                # Parent formset's queryset, optionally filtered and ordered
                qs = super(PaginatedFormSet, self).get_queryset()
                if obj is not None:
                    fk_name = self.fk.name
                    qs = qs.filter(**{fk_name: obj})
                # Ensure deterministic ordering to avoid duplicates across pages
                if 'id' not in self.ordering and 'pk' not in self.ordering:
                    return qs.order_by(*self.ordering, 'pk')
                return qs.order_by(*self.ordering)

            @cached_property
            def paginator(self):
                return Paginator(self.base_queryset, self.per_page)

            @cached_property
            def page_obj(self):
                page_num = request.GET.get(f"{self.pagination_key}_page", 1)
                try:
                    page_num = int(page_num)
                except (TypeError, ValueError):
                    page_num = 1
                return self.paginator.get_page(page_num)

            def get_queryset(self):
                # Return only the current page's slice as a QuerySet
                start = self.page_obj.start_index() - 1
                end = self.page_obj.end_index()
                return self.base_queryset[start:end]

        return PaginatedFormSet
