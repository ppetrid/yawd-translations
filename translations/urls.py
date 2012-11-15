import re
from django.conf.urls import patterns
from django.conf import settings
from django.core.urlresolvers import LocaleRegexURLResolver
from utils import get_default_language
from django.utils.translation import get_language

def translation_patterns(prefix, *args):
    """
    Custom pattern declaration that works like the i18n_patterns but
    matches root urls if the default language is active.
    Adds the language code prefix to every URL pattern within this
    function.
    """
    pattern_list = patterns(prefix, *args)
    if not settings.USE_I18N:
        return pattern_list
    return [TranslationRegexURLResolver(pattern_list)]
           
class TranslationRegexURLResolver(LocaleRegexURLResolver):
    """
    A URL resolver that always matches the active language code as URL prefix.

    Rather than taking a regex argument, we just override the ``regex``
    function to always return the active language-code as regex.
    """

    @property
    def regex(self):
        if get_language() == get_default_language():
            return re.compile(r'')
        return super(TranslationRegexURLResolver, self).regex