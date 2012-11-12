import re
from django.core.urlresolvers import is_valid_path, get_resolver
from django.middleware.locale import LocaleMiddleware
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from utils import get_default_language, get_language_from_request
from urls import TranslationRegexURLResolver

class TranslationMiddleware(LocaleMiddleware):
    """
    This subclasses the original django LocaleMiddleware. 
    It is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context. This allows pages to be dynamically
    translated to the language the user desires (if the language
    is available, of course).
    """

    def process_request(self, request):
        check_path = self.is_language_prefix_patterns_used()

        #replace the original language detection method
        language = get_language_from_request(
            request, check_path=check_path)

        default = get_default_language()
        translation.activate(language)

        #redirect to the original default language URL
        #if language prefix is used
        if (check_path and default == language and 
            request.path_info.startswith('/%s/' % default)):
            urlconf = getattr(request, 'urlconf', None)
            language_path = re.sub(r'^/%s/' % default, '/', request.path_info)
            if settings.APPEND_SLASH and not language_path.endswith('/'):
                language_path = language_path + '/'

            if is_valid_path(language_path, urlconf):
                #we use a permanent redirect here.
                #when changing the default language we need to let the world know
                #that our links have permanently changed and transfer our seo juice 
                #to the new url
                #http://seo-hacker.com/301-302-redirect-affect-seo/
                return  HttpResponsePermanentRedirect("%s://%s/%s" % (
                    request.is_secure() and 'https' or 'http',
                    request.get_host(), re.sub(r'^/%s/' % default, '', request.get_full_path())))
        
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()
        
        #original django middleware used to redirect 404 responses to a 
        #language-dependend url if language prefix patterns were used  
        #this behavior is removed from yawd-translations
         
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language
        return response