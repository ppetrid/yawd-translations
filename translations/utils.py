from django.conf import settings
from django.utils.translation import check_for_language
from django.utils.translation.trans_real import get_language_from_path

_default = None
_supported = []

def get_default_language():
	"""
	Detects the default language from the database.
	If no default language is present, the default
	settings.LANGUAGE_CODE is used.
	
	This will reload its values in the context of a new thread.
	"""
	global _default
	
	if _default is None:
		try:
			from models import Language
			_default = Language.objects.get(default=True).name
		except:
			_default = settings.LANGUAGE_CODE

	return _default

def get_supported_languages():
	"""
	This will retrieve the supported languages.
	"""
	global _supported
	
	if not _supported:
		from models import Language
		_supported = list(Language.objects.values_list('name', flat=True))

		#if no languages are set use the default language
		if not _supported:
			_supported = [settings.LANGUAGE_CODE]

	return _supported

def get_language_from_request(request, check_path=False):
	"""
	This method is used as a replacement to the original django language 
    detection algorithm. It takes the db default language into 
    consideration and does not deal with the Accept-Language header.
    
    Analyzes the request to find what language the user wants the system to
    show. Only languages listed in settings.LANGUAGES are taken into account.
    If the user requests a sublanguage where we have a main language, we send
    out the main language.

    If check_path is True, the URL path prefix will be checked for a language
    code, otherwise this is skipped for backwards compatibility.
    """
	#retrieve list of supported languages
	supported = get_supported_languages()

	if check_path:
		lang_code = get_language_from_path(request.path_info, [settings.LANGUAGE_CODE].append(supported))
		if lang_code is not None:
			return lang_code

	if hasattr(request, 'session'):
		lang_code = request.session.get('django_language', None)
		if lang_code in supported and lang_code is not None and check_for_language(lang_code):
			return lang_code

	lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

	if lang_code and lang_code not in supported:
		lang_code = lang_code.split('-')[0] # e.g. if fr-ca is not supported fallback to fr

	if lang_code and lang_code in supported and check_for_language(lang_code):
		return lang_code

	#original Django middleware used to look for the Accept-Language 
	#HTTP header and extract the language. This is replaced in our
	#mechanism
	return get_default_language()