from django.contrib import admin
from translations.admin import TranslationInline
from models import MultilingualPage, MultilingualPageTranslation

class MultilingualPageTranslationAdmin(TranslationInline):
    model =  MultilingualPageTranslation

class MultilingualPageAdmin(admin.ModelAdmin):
    inlines = [MultilingualPageTranslationAdmin]

admin.site.register(MultilingualPage, MultilingualPageAdmin)