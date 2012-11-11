from django.db import models
from translations.models import Translatable, Translation

class MultilingualPage(Translatable):
    #this field will be available "as is" in all languages
    slug = models.SlugField(max_length=100)
    
    @models.permalink
    def get_absolute_url(self):
        return ('multilingual-page-view', (), {'slug' : self.slug })
    
class MultilingualPageTranslation(Translation):
    #these fields can be translated
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    #relate MultilingualPageTranslation with MultilingualPage
    #the reverse relation must be named 'translations'
    page = models.ForeignKey(MultilingualPage, related_name='translations')

    def __unicode__(self):
        return u'%s' % self.title
        
    
    