from django.forms.models import BaseInlineFormSet
from models import Language

class BaseTranslationFormSet(BaseInlineFormSet):
    """
    This implements the default formset that should be used with translatable objects.
    """
    def __init__(self, *args, **kwargs):
        #calculate a queryset that retrieves all non-translated languages
        #for this instance 
        if 'instance' in kwargs and kwargs['instance']:
            queryset = Language.objects.exclude(
                name__in=kwargs['instance'].translations.values_list(
                    'language_id', flat=True)).values_list(
                        'name', flat=True)
        else:
            queryset = Language.objects.values_list('name', flat=True)

        #provide initial data based on untranslated languages
        kwargs['initial'] = [ {'language' : x} for x in queryset]
        #should not allow more inlines than that of the number of languages
        self.max_num = Language.objects.count()

        super(BaseTranslationFormSet, self).__init__(*args, **kwargs)