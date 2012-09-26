import os, shutil
from django.conf import settings
from django.views.generic import TemplateView
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.importlib import import_module
from django.utils.text import capfirst
from django.utils.translation import to_locale, ugettext as _, get_language_info
from models import Language

#TODO: Permissions

class GenerateTranslationMessagesView(TemplateView):
    template_name ='admin/includes/translation_messages_list.html'
    
    def get(self, request, *args, **kwargs):

        try:
            self.language = Language.objects.get(name=args[0])
        except Language.DoesNotExist:
            raise Http404
        
        if settings.LOCALE_PATHS:
            #check if the folder for this language exists and attempt to create it if id does not exist
            self.po_path = os.path.join(settings.LOCALE_PATHS[0], to_locale(self.language.name), 'LC_MESSAGES')
            if not os.path.exists(self.po_path):
                try:
                    os.makedirs(self.po_path)
                except:
                    self.error = _('Could not create the target folder.')
        else:
            self.error = _('<b>Configuration error!</b> Please set the LOCALE_PATHS project setting to allow the creation of a unified messages catalog.')
        
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super(GenerateTranslationMessagesView, self).get_context_data(**kwargs)
        
        if hasattr(self, 'error') and self.error:
            context['error'] = self.error
            return context
        
        lang_files = []
        #iterate over the installed applications and copy their po files
        #for this language to the appropriate folder 
        for app_name in settings.INSTALLED_APPS:    
            mod = import_module(app_name)
            original_path = os.path.join(os.path.dirname(mod.__file__), 'locale', to_locale(self.language.name), 'LC_MESSAGES')
            
            if os.path.exists(original_path):
                #iterate over the availale po files
                for file_ in os.listdir(original_path):
                    if file_.endswith('.po'):
                        file_name = '%s-%s' % (app_name, file_)
                        file_path = os.path.join(self.po_path, file_name)
                        #copy the file if it does not exist
                        if not os.path.exists(file_path):
                            shutil.copy2(os.path.join(original_path, file_), file_path)
                        lang_files.append(file_name)

        context['lang_files'] = lang_files
        return context
    

class TranslationMessagesView(TemplateView):
    template_name = 'admin/translation_messages.html'
    
    def get(self, request, *args, **kwargs):

        try:
            self.language = Language.objects.get(name=args[0])
        except Language.DoesNotExist:
            raise Http404

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context) 
    
    def get_context_data(self, **kwargs):
        context = super(TranslationMessagesView, self).get_context_data(**kwargs)
        
        context['title'] = _('Translate Static Messages')
        context['language'] = self.language
        context['app_label'] = self.language._meta.app_label
        context['module_name'] = capfirst(force_unicode(self.language._meta.verbose_name_plural))
        
        if not settings.LOCALE_PATHS:
            context['error'] = _('<b>Configuration error!</b> Please set the LOCALE_PATHS project setting to allow the creation of a unified messages catalog.')
            return context
        
        context['lang_files'] = []
        po_path = os.path.join(settings.LOCALE_PATHS[0], to_locale(self.language.name), 'LC_MESSAGES')
        if os.path.exists(po_path):
            for file_ in os.listdir(po_path):
                if file_.endswith('.po'):
                    context['lang_files'].append(file_)
        else:
            context['warning'] = _('The system does not appear to have any translation messages for this language. Please use the "Generate messages" button.')
        return context
        
        