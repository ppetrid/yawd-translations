import re
from django.utils.translation import get_language
from django.conf import settings
from models import Language
from utils import get_default_language

lang_pattern = '|'.join([i[0] for i in settings.LANGUAGES])

def languages(request):
    """
    This context processor adds three context variables::
    
        `langs`:    A list of the available project languages. This list holds :class:`translations.models.Language` instances.
        `default`:    The default language. This holds the **language** code and not the :class:`translations.models.Language` instance.
        `clean_url`:    The current url with the preceding language code (if there is one) removed. E.g. for the url `'/en/whatever/'` the ``clean_url`` will be `'/whatever/'`. Useful if the project URLs have common slugs etc. and we want to avoid reversing views in our templates in order to find the equivalent url of another language.  
    """
    langs = Language.objects.all()
    default = get_default_language()
    
    #assumes that no name collisions exist
    clean_url = re.sub('/%s/' % default, '/', request.path) if get_language() == default else re.sub(r'^/(%s)/' % lang_pattern, '/', request.path)

    return {
        'langs' : langs,
        'default_lang': default,
        'clean_url' : clean_url
    }