import re
from django.utils.translation import get_language
from django.conf import settings
from models import Language
from utils import get_default_language

lang_pattern = '|'.join([i[0] for i in settings.LANGUAGES])

def languages(request):

    langs = Language.objects.all()
    default = get_default_language()
    
    #assumes that no name collisions exist
    clean_url = re.sub('/%s/' % default, '/', request.path) if get_language() == default else re.sub(r'^/(%s)/' % lang_pattern, '/', request.path)

    return {
        'langs' : langs,
        'default_lang': default,
        'clean_url' : clean_url
    }