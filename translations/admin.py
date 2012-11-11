from django.contrib import admin
from django.conf.urls import patterns, url
from django.forms import HiddenInput
from django.forms.models import modelformset_factory
from django.utils.translation import ungettext, ugettext_lazy
from models import Language
from forms import BaseTranslationFormSet
from views import TranslationMessagesView, GenerateTranslationMessagesView, TranslationMessagesEditView

class TranslationInline(admin.StackedInline):
    template = 'admin/edit_inline/translatable-inline.html'
    
    def __init__(self, *args, **kwargs):
        super(TranslationInline, self).__init__(*args, **kwargs)
        self.formset = modelformset_factory(self.model, formset=BaseTranslationFormSet)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(TranslationInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name  == 'language':
            formfield.widget = HiddenInput()
        return formfield

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'default')
    actions=['delete_selected_lang']
    #yawdcms-specific metas
    order = 100
    separator = True
    
    def get_urls(self):
        """
        Override get_urls to include the translation messages view
        for the specified language
        """
        urls = super(LanguageAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^(.+)/messages/$', self.admin_site.admin_view(TranslationMessagesView.as_view()), name="translations-messages-view"),
            url(r'^(.+)/messages/generate/$', self.admin_site.admin_view(GenerateTranslationMessagesView.as_view()), name="generate-translations-messages-view"),
            url(r'^(.+)/messages/(.+)/$', self.admin_site.admin_view(TranslationMessagesEditView.as_view()), name="edit-translations-messages-view"),
        )
        return my_urls + urls
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return True

    def get_actions(self, request):
        actions = super(LanguageAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_selected_lang(self, request, queryset):
        queryset = queryset.exclude(default=True)
        count = queryset.count()
        queryset.delete()
        
        self.message_user(request, ungettext(
            '%(count)d non-default language was deleted',
            '%(count)d non-default languages were deleted',
            count) % {
                'count': count,
        })
    delete_selected_lang.short_description = ugettext_lazy("Delete selected languages")
    
admin.site.register(Language, LanguageAdmin)