from django import template
from django.utils.translation import get_language, activate
from translations.models import Translatable, Language
from translations.utils import get_default_language

register = template.Library()

@register.inclusion_tag('language_switcher.html', takes_context=True)
def translation_urls(context, object_=None):
    """
    This simple tag returns the urls of a translatable object
    if get_absolute_url is implemented. For languages that do not
    have a translation for this object, it redirects to the language's
    home page.
    """
    current_language = get_language()
    #use the translations.context_processors.languages context processor if
    #available, to avoid extra queries
    langs = context['langs'] if 'langs' in context else Language.objects.all()
    urls = [] 
    
    for lang in langs:
        activate(lang.pk)
        url = '/%s/' % lang.pk if not lang.default else '/'
        
        if object_ and hasattr(object_, 'get_absolute_url'):
            url = object_.get_absolute_url()
        elif isinstance(object_, Translatable):
            translation = object_.translation()
            if translation and hasattr(translation, 'get_absolute_url'):
                url = translation.get_absolute_url()
        
        urls.append({'language' : lang, 'url' : url if url else '/%s/' % lang.pk })

    activate(current_language)
    return { 'urls' : urls }