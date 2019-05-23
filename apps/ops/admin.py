from django.contrib import admin
from django.db import models
from .models import *

# Register your models here.

class CommonAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs): # 强制用CharField用TextArea的UI
        formfield = super(CommonAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ('Description', 'Material', 'Manual', 'Text', 'image_paths', 'Tip', 'Nutrition', 'Efficacy', 'Goodfor', 'Badfor', 'Shoptip'):
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield
    list_per_page = 20
    ordering = ['-pk']
    # search_fields = ('Name',)
    show_full_result_count = False # 在过滤的结果页面 99 results (103 total) 变成 99 results (Show all)
    # list_display_links = ('pk', 'Name')
    def image_tag(self, obj):
        url = obj.image_paths.split('\n')[0]
        return format_html(f'''<img height="48" width="48" src='{settings.MEDIA_URL}/image/{url}'>''')
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True
    # c自定义模板hange_form_template = 'change_form.html' # 自定义模板


@admin.register(CommandExecution)
class CommandExecutionAdmin(CommonAdmin):
    list_display = [fd.name for fd in CommandExecution._meta.get_fields() if type(fd) is not models.ManyToManyField ]
    ordering = ['-date_created']
@admin.register(CeleryTask)
class CeleryTaskAdmin(CommonAdmin):
    list_display = [fd.name for fd in CeleryTask._meta.get_fields() if type(fd) is not models.ManyToManyField ]
@admin.register(Task)
class TaskAdmin(CommonAdmin):
    list_display = [fd.name for fd in Task._meta.get_fields() if type(fd) is not models.ManyToManyField ]
@admin.register(AdHoc)
class AdHocAdmin(CommonAdmin):
    list_display = [fd.name for fd in AdHoc._meta.get_fields() if type(fd) is not models.ManyToManyField ]
@admin.register(AdHocRunHistory)
class AdHocRunHistoryAdmin(CommonAdmin):
    list_display = [fd.name for fd in AdHocRunHistory._meta.get_fields() if type(fd) is not models.ManyToManyField ]
