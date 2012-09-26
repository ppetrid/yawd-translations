from django.contrib import admin
from django.conf.urls import patterns, url
from django.utils.translation import ungettext, ugettext_lazy
from models import Language
from views import TranslationMessagesView, GenerateTranslationMessagesView

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
            url(r'^(.+)/messages/$', TranslationMessagesView.as_view(), name="translations-messages-view"),
            url(r'^(.+)/messages/generate/$', GenerateTranslationMessagesView.as_view(), name="generate-translations-messages-view")
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