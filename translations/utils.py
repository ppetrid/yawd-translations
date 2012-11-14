import locale, os, sys
from django.conf import settings
from django.utils.translation import check_for_language
from django.utils.encoding import smart_str 
from django.utils.translation.trans_real import get_language_from_path, to_locale

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
			_default = smart_str(Language.objects.get(default=True).name)
		except:
			_default = settings.LANGUAGE_CODE

	return _default

def get_supported_languages():
	"""
	Retrieve the supported languages.
	"""
	global _supported
	
	if not _supported:
		from models import Language
		_supported = [smart_str(l) for l in Language.objects.values_list('name', flat=True)]

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

def compile_message_file(fn):
	"""
	Accepts a .po file path as argument and generates an appropriate .mo file.
	This copies the needed functionality from the original compilemessages command
	"""
	
	pf = os.path.splitext(fn)[0]
	# Store the names of the .mo and .po files in an environment
	# variable, rather than doing a string replacement into the
	# command, so that we can take advantage of shell quoting, to
	# quote any malicious characters/escaping.
	# See http://cyberelk.net/tim/articles/cmdline/ar01s02.html
	os.environ['djangocompilemo'] = pf + '.mo'
	os.environ['djangocompilepo'] = pf + '.po'
	if sys.platform == 'win32': # Different shell-variable syntax
		cmd = 'msgfmt --check-format -o "%djangocompilemo%" "%djangocompilepo%"'
	else:
		cmd = 'msgfmt --check-format -o "$djangocompilemo" "$djangocompilepo"'
	os.system(cmd)
	os.chmod(pf + '.mo', 0664)
	
def concat_message_files(files, fn):
	"""
	Accepts a list of po files and a target file and uses the
	msgcat command to concat the files.
	"""

	files_str = ' '.join(files)

	os.environ['djangosourcepo'] = files_str
	os.environ['djangotargetpo'] = fn
	
	if sys.platform == 'win32': # Different shell-variable syntax
		cmd = 'msgcat --use-first -o "%djangotargetpo%" %djangosourcepo%'
	else:
		cmd = 'msgcat --use-first -o "$djangotargetpo" $djangosourcepo'
	os.system(cmd)
	os.chmod(fn, 0664)
	
def reset_translations(lang):
	"""
	Empty django's internal translations dictionary when a message translation
	changes or the translations list is regenerated.
	"""
	from django.utils import translation
	from django.utils.translation import trans_real
	import gettext
	
	if lang in trans_real._translations:
		del trans_real._translations[lang]
	
	gettext._translations = {}

	if settings.LANGUAGE_CODE == lang:
		trans_real._default = None
	
	#force current thread translations reload
	current_lang = translation.get_language()
	if current_lang == lang:
		translation.activate(current_lang)