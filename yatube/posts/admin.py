from django.contrib import admin

from yatube.settings import YATUBE_CONST

from .models import Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    # list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = YATUBE_CONST['empty']
    list_select_related = ('author', 'group')
    # list_per_page = 30
    actions_on_bottom = True
    actions = ['group_1', 'group_2', 'group_3']

    def group_1(self, request, queryset):
        queryset.update(group='1')
    group_1.short_description = 'all_group_1'

    def group_2(self, request, queryset):
        queryset.update(group='2')
    group_2.short_description = 'all_group_2'

    def group_3(self, request, queryset):
        queryset.update(group='3')
    group_3.short_description = 'all_group_3'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'description')
    search_fields = ('slug', 'title')
    empty_value_display = YATUBE_CONST['empty']


admin.site.disable_action('delete_selected')
