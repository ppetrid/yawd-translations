from django import forms
from django.forms.models import BaseInlineFormSet
from models import Language
from utils import get_supported_languages

class BaseTranslationFormSet(BaseInlineFormSet):
    """
    This implements the default formset that should be used with translatable objects.
    """
    #the reverse name to use in order to get the translations from the originating object
    translations_property = 'translations'

    def __init__(self, *args, **kwargs):
        #calculate a queryset that retrieves all non-translated languages
        #for this instance 
        if 'instance' in kwargs and kwargs['instance']:
            #translations.all() is already prefetched, so we iterate over it to avoid the join
            queryset = Language.objects.exclude(name__in=[l.language_id \
                    for l in getattr(kwargs['instance'],
                                     self.translations_property).all()]) \
                               .values_list('name', flat=True)
        else:
            #we do not use get_supported_language as this method
            #might return the default django LANGUAGE setting.
            queryset = Language.objects.values_list('name', flat=True)

        #provide initial data based on untranslated languages
        kwargs['initial'] = [ {'language' : x} for x in queryset]
        #should not allow more inlines than that of the number of languages
        self.max_num = len(get_supported_languages())
        self.extra = len(kwargs['initial']) 

        super(BaseTranslationFormSet, self).__init__(*args, **kwargs)
        
class PoFileForm(forms.Form):
    po_content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'textarea-full'}))
