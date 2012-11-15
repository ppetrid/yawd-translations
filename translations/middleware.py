import re
from django.conf import settings
from django.core.urlresolvers import is_valid_path, get_resolver
from django.http import HttpResponsePermanentRedirect
from django.middleware.locale import LocaleMiddleware
from django.utils.cache import patch_vary_headers
from django.utils import translation
from utils import get_default_language, get_language_from_request, get_supported_languages

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
        """
        Enable the default language if a supported db language can not
        be resolved.
        """
        #replace the original language detection method
        language = get_language_from_request(
            request, check_path=self.is_language_prefix_patterns_used())
        
        if language not in get_supported_languages():
            language = get_default_language()

        translation.activate(language)        
        request.LANGUAGE_CODE = translation.get_language()
        
        
    def process_response(self, request, response):
        """
        Override the original method to redirect permanently and facilitate 
        the :func.`translations.urls.translation_patterns` URL redirection
        logic.
        """
        language = translation.get_language()
        default = get_default_language()
        
        #redirect to the original default language URL
        #if language prefix is used
        if (response.status_code == 404 and
            self.is_language_prefix_patterns_used() and default == language and 
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
                #http://blog.yawd.eu/2012/impact-django-page-redirects-seo/
                return  HttpResponsePermanentRedirect("%s://%s/%s" % (
                    request.is_secure() and 'https' or 'http',
                    request.get_host(), re.sub(r'^/%s/' % default, '', request.get_full_path())))
        
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language
        return response