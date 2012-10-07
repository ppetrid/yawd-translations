from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import clear_url_caches
from django.db import models
from django.db.models.signals import pre_delete, post_delete
from django.utils.translation import get_language, get_language_info, ugettext as _
from elfinder.fields import ElfinderField
import utils

class Language(models.Model):
    #Use name as primary key to avoid joins when retrieving Translation objects
    name = models.CharField(choices=sorted(settings.LANGUAGES, key=lambda name: name[1]), max_length=7, primary_key=True)
    image = ElfinderField(optionset='image', start_path='languages')
    default = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        permissions = (
            ("view_translations", "Can see translation messages for a language"),
            ("edit_translations", "Can edit the language's translation messages"),
        )

    def save(self, *args, **kwargs):
        if self.default: #make sure only one default language exists
            try: 
                default = Language.objects.get(default=True)
                if self != default:
                    default.default = False
                    default.save()
            except Language.DoesNotExist:
                pass

            ##Change the default language for this thread
            clear_url_caches()
            utils._default = self.name 

        super(Language, self).save(*args, **kwargs)
        #this might produce a little overhead, but it's necessary
        #since after model changes the state of _supported could be unpredicatble
        utils._supported = Language.objects.values_list('name', flat=True)

    def delete(self):
        """
        Deleting the default language is not allowed.
        """
        if not self.default:
            super(Language, self).delete()

    def __unicode__(self):
        return get_language_info(self.name)['name']

class Translatable(models.Model):
    class Meta:
        abstract = True
        
    def _get_cache_key(self, language):
        return '%s::%s::%s' % (self.__class__.__name__, self.id, language)
    
    def _get_name(self, language, translation):
        """
        Calculate the Translatable object's translation name.
        """
        try:
            return unicode(self.translations.get(language_id=language) if not translation else translation)
        except ObjectDoesNotExist:
            try: #attempt to show default translation
                return u'%s (%s %s)' % (unicode(self.translations.get(language__default=True)), translation.ugettext('not translated in'), language)
            except ObjectDoesNotExist:
                return u'%s #%s (%s %s)' % (self._meta.verbose_name, self.id, translation.ugettext('not translated in'), language)
            
    def get_name(self, language=None, translation=None):
        """
        Get the Translatable object's display name for a given
        language or translation.
        """

        #use the current language if not explicitly set
        if not language:
            language = translation.language_id if translation else get_language()
            
        key = self._get_cache_key(language)

        name = cache.get(key)

        if not name: #not in cache
            name = self._get_name(language, translation)
            cache.set(key, name)

        return name
    
    def update_name(self, language=None, translation=None):
        cache.delete(self._get_cache_key(translation.language_id if translation else language))
        self.get_name(language=language, translation=translation)
        
    def __unicode__(self):
        return self.get_name()
        
class Translation(models.Model):
    language = models.ForeignKey(Language)
    
    class Meta:
        abstract = True
    
    @property
    def translatable(self):
        raise NotImplementedError
  
    def save(self):
        super(Translation, self).save()
        #update the display name for this language
        self.translatable.update_name(translation=self)
        
def pre_delete_language(sender, instance, using, **kwargs):
    #admin actions make sure the default will not be deleted, so yawdcms does not directly need this
    #this is here to prevent 3rd party code from accidentily deleting the default language  
    if instance.default:
        raise Exception(_("Cannot delete the default language"))

def post_delete_language(sender, instance, using, **kwargs):
    """
    Update the supported languages to ensure that 
    a 404 will be raised when requestng the language's urls
    """
    utils._supported.remove(instance.name)
    
pre_delete.connect(pre_delete_language, sender=Language, dispatch_uid='language-pre-delete')
post_delete.connect(post_delete_language, sender=Language, dispatch_uid='language-post-delete')