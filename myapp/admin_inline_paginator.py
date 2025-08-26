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

            @cached_property
            def queryset(self):
                # Filter by parent object if editing an instance
                qs = super(PaginatedFormSet, self).queryset
                if obj is not None:
                    fk_name = self.fk.name
                    qs = qs.filter(**{fk_name: obj})
                return qs.order_by(*getattr(self, 'ordering', ['id']))

            @cached_property
            def paginator(self):
                return Paginator(self.queryset, self.per_page)

            @cached_property
            def page_obj(self):
                page_num = request.GET.get(f"{self.pagination_key}_page", 1)
                return self.paginator.get_page(page_num)

            def _construct_forms(self):
                self.forms = []
                # Slice queryset manually for current page
                start = self.page_obj.start_index() - 1
                end = self.page_obj.end_index()
                page_queryset = list(self.queryset[start:end])
                for i, obj_instance in enumerate(page_queryset):
                    self.forms.append(self._construct_form(i, instance=obj_instance))
                # No extra forms
                # self.forms += [self._construct_form(i + len(page_queryset)) for i in range(self.extra)]

            def __iter__(self):
                if not hasattr(self, "forms") or not self.forms:
                    self._construct_forms()
                return iter(self.forms)

            def __len__(self):
                if not hasattr(self, "forms") or not self.forms:
                    self._construct_forms()
                return len(self.forms)

        return PaginatedFormSet
