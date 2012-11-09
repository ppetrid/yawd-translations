from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import clear_url_caches
from django.db import models
from django.db.models.signals import pre_delete, post_delete
from django.utils.encoding import smart_str 
from django.utils.translation import get_language, get_language_info, ugettext_lazy, ugettext as _
from elfinder.fields import ElfinderField
import utils

class Language(models.Model):
    #Use name as primary key to avoid joins when retrieving Translation objects
    name = models.CharField(choices=sorted(settings.LANGUAGES, key=lambda name: name[1]), max_length=7, verbose_name=ugettext_lazy('Name'), primary_key=True)
    image = ElfinderField(optionset='image', start_path='languages', verbose_name=ugettext_lazy('Image'), blank=True)
    default = models.BooleanField(default=False, verbose_name=ugettext_lazy('Default'))

    class Meta:
        verbose_name = ugettext_lazy("Language")
        verbose_name_plural = ugettext_lazy("Languages")
        ordering = ['name']
        permissions = (
            ("view_translations", "Can see translation messages for a language"),
            ("edit_translations", "Can edit the language's translation messages"),
        )
        
    def _default_changed(self):
        #change the default language for this thread
        clear_url_caches()
        utils._default = self.name

    def save(self, *args, **kwargs):
        try:
            #not using get_default_language() here, as this method might return
            #the settings.LANGUAGE_CODE setting if no db languages exist
            default = Language.objects.get(default=True)
            #check if the default language just changed
            if self.default and self != default:
                #make sure only one default language exists
                default.default = False
                default.save()
                self._default_changed()

        except Language.DoesNotExist:
            #no default language was found
            #force this as the default
            self.default = True
            self._default_changed()

        super(Language, self).save(*args, **kwargs)
        #this might produce a little overhead, but it's necessary:
        #the state of _supported could be unpredictable by now
        utils._supported = [smart_str(l) for l in Language.objects.values_list('name', flat=True)]

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
                return u'%s (%s %s)' % (unicode(self.translations.get(language__default=True)), _('not translated in'), language)
            except ObjectDoesNotExist:
                return u'%s #%s (%s %s)' % (self._meta.verbose_name, self.id, _('not translated in'), language)
            
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
        """
        Updates the cached display name for this object. Typically, 
        this will be called whenever a translation changes.
        """
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
    #admin actions make sure the default will not be deleted,
    #but this is still here to prevent 3rd party code from accidentily deleting the default language  
    if instance.default:
        raise Exception(_("Cannot delete the default language"))

def post_delete_language(sender, instance, using, **kwargs):
    """
    Update the supported languages to ensure that 
    a 404 will be raised when requesting the language's urls
    """
    #generate supported languages in case they are not initialized
    utils.get_supported_languages()
    utils._supported.remove(instance.name)
    
pre_delete.connect(pre_delete_language, sender=Language, dispatch_uid='language-pre-delete')
post_delete.connect(post_delete_language, sender=Language, dispatch_uid='language-post-delete')