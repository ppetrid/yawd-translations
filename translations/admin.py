from django.contrib import admin
from django.conf.urls import patterns, url
from django.forms import HiddenInput
from django.forms.models import modelformset_factory
from django.utils.translation import ungettext, ugettext_lazy
from models import Language, Translation
from forms import BaseTranslationFormSet
from views import TranslationMessagesView, GenerateTranslationMessagesView, TranslationMessagesEditView

class TranslationInline(admin.StackedInline):
    """
    This is a custom inline class that will display one form for each available
    language.
    """
    template = 'admin/edit_inline/translatable-inline.html'
    
    def __init__(self, *args, **kwargs):
        super(TranslationInline, self).__init__(*args, **kwargs)
        if not issubclass(self.model, Translation):
            raise Exception('This inline should only be used with Translation models')
        self.formset = modelformset_factory(self.model, formset=BaseTranslationFormSet)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Override the ``formfield_for_dbfield()`` method to make the `'language'`
        property of the :class:`translations.models.Translation` object hidden.
        """
        formfield = super(TranslationInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name  == 'language':
            formfield.widget = HiddenInput()
        return formfield

class LanguageAdmin(admin.ModelAdmin):
    """
    The default admin form for the :class:`translations,models.Language` model.
    """
    list_display = ('name', 'default')
    actions=['delete_selected_lang']
    fields = ('name', 'image', 'default')
    #this is used only when yawd-admin is being used, ignored otherwise
    title_icon = 'icon-flag'
    
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
        """
        Check if language is the default and deny deletion access if True.
        """
        return False if obj and obj.default else True

    def get_actions(self, request):
        """
        Remove the original `delete action` that allows a user to delete
        a default ``Language``.
        """
        actions = super(LanguageAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
    
    def get_readonly_fields(self, request, obj=None):
        """
        Override to make certain language name readonly if this is a change request.
        """
        if obj is not None:
            return self.readonly_fields + ('name',)
        return self.readonly_fields

    def delete_selected_lang(self, request, queryset):
        """
        This delete action will ensure that the default language will not
        be deleted.
        """
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