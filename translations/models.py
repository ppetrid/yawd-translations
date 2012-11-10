from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import clear_url_caches
from django.db import models
from django.db.models.signals import pre_delete, post_delete
from django.utils.encoding import smart_str 
from django.utils.translation import get_language, get_language_info, ugettext_lazy, ugettext as _
from elfinder.fields import ElfinderField
from managers import TranslatableManager
import utils

class Language(models.Model):
    """
    This model stores the project's available languages. A user may edit
    languages from the admin interface. At least one language
    must always be stored in the database. One (and only one) language
    must always be set as the 'default'. Methods of this model and other
    aspects of yawd-translations guarantee that these constraints are
    always met.
    
    The languages among which a user may choose are those defined in the
    `LANGUAGES <https://docs.djangoproject.com/en/dev/ref/settings/#languages>`_
    django setting. 
    """
    
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
    """
    This model should be subclassed by models that need multilingual
    support.
    
    A Translatable object should only define members
    that are **common** to all languages. To define multilingual
    fields, a subclass of the :class:`translations.models.Translation`
    model must be implemented. 
    """
    objects = TranslatableManager()
    
    class Meta:
        abstract = True        

    def get_name(self, language_id=None):
        """
        Get the related :class:`translations.models.Translation`
        object's display name for a given ``language``.
        """
        #use the current language if not explicitly set
        translation = unicode(self.translation(language_id))
        if translation:
            return translation

        #attempt to show default translation
        translation = unicode(self.translation(get_default_language()))  
        if translation:
            return u'%s (%s %s)' % (translation, _('not translated in'), language_id)
        else:
            return u'%s #%s (%s %s)' % (self._meta.verbose_name, self.id, _('not translated in'), language_id)

    def translation(self, language_id=None):
        """
        Get translation for the language ``language_id``. If no argument
        is given, return the current language translation.
        
        Always use this method if you need to access a translation,
        since it does not generate extra queries.
        """
        if not language_id:
            language_id = get_language()
        #using prefetched translations
        for l in self.translations.all():
            if l.language_id == language_id:
                return l
        
    def __unicode__(self):
        """
        Default implementation returns the unicode representation of
        the related :class:`translations.models.Translation` object
        for the current language.
        """
        return self.get_name()
        
class Translation(models.Model):
    language = models.ForeignKey(Language)
    
    class Meta:
        abstract = True
        
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