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
            ordering = getattr(self, 'ordering',['id'])

            @cached_property
            def base_queryset(self):
                # Filter by parent object if editing an instance
                qs = super(PaginatedFormSet, self).get_queryset()
                if obj is not None:
                    fk_name = self.fk.name
                    qs = qs.filter(**{fk_name: obj})
                return qs.order_by(*self.ordering)

            @cached_property
            def paginator(self):
                return Paginator(self.base_queryset, self.per_page)

            @cached_property
            def page_obj(self):
                page_num = request.GET.get(f"{self.pagination_key}_page", 1)
                return self.paginator.get_page(page_num)

            @cached_property 
            def page_queryset(self):   
                # Use paginator's object_list for the current page to avoid index math issues
                return list(self.page_obj.object_list)
            
            def _construct_forms(self):
                self._forms = []
                for i, obj_instance in enumerate(self.page_queryset):
                    self._forms.append(self._construct_form(i, instance=obj_instance))
            
            def initial_form_count(self):
                return len(self.page_queryset)       
            
            def total_form_count(self):
                return len(self.page_queryset)

        return PaginatedFormSet

