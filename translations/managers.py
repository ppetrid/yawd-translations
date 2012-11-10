from django.db import models

class TranslatableManager(models.Manager):
    """
    Override the default manager for
    :class:`translations.models.Translatable` objects to prefetch
    the related :class:`translations.models.Translation` translations.
    
    This way we can exploit the queryset cache to minimize database
    hits. 
    """
    use_for_related_fields = True
    
    def get_query_set(self):
        return super(TranslatableManager, self).get_query_set().prefetch_related('translations')
        
    