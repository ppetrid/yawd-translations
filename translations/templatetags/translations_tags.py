from django import template
from django.utils.translation import get_language, activate
from translations.models import Translatable, Language


register = template.Library()


@register.inclusion_tag('language_switcher.html', takes_context=True)
def translation_urls(context, object_=None):
    """
    This simple tag returns all language urls of an object
    if get_absolute_url is implemented. For languages that do not
    have a translation for this object, it redirects to the language's
    home page.
    
    If ``object_`` is a string, the tag assumes its a URL and will just
    prepend the appropriate language prefix.
    """
    current_language = get_language()
    #use the translations.context_processors.languages context processor if
    #available, to avoid extra queries
    langs = context['langs'] if 'langs' in context else Language.objects.all()
    urls = [] 
    
    for lang in langs:
        activate(lang.pk)
        url = ''

        if object_ and hasattr(object_, 'get_absolute_url'):
            url = object_.get_absolute_url()
        elif isinstance(object_, Translatable):
            translation = object_.translation()
            if translation and hasattr(translation, 'get_absolute_url'):
                url = translation.get_absolute_url()
        elif isinstance(object_, str) or isinstance(object_, unicode):
            url = '/%s%s' % (lang.pk, object_) if not lang.default else object_
 
        #in case there is no url for this language redirect to the
        #language's index page
        if not url: 
            url = '/%s/' % lang.pk if not lang.default else '/'

        urls.append({'language': lang, 'url': url })

    activate(current_language)
    return { 'urls' : urls }
