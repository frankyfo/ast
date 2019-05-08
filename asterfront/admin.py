from django.contrib import admin
from models import BlackListed
# Register your models here.
def delete_numbers(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()

class BlackListAdmin(admin.ModelAdmin):
    list_display = ('number', 'cause', 'creator')
    actions = [delete_numbers]

    def get_actions(self, request):
        actions = super(BlackListAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(BlackListed, BlackListAdmin)