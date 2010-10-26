"""
Database model for django-enterprise-cms
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from django.conf import settings
from django.core.validators import validate_slug
from django.utils.translation import ugettext_lazy as _
from django.forms.models import model_to_dict

from ecms.managers import CmsObjectManager


# -------- Init code --------


import mptt
try:
    # MPTT 0.4
    from mptt.models import MPTTModel
except ImportError:
    # MPTT 0.3
    MPTTModel = models.Model


def _get_current_site():
    id = settings.SITE_ID
    try:
        return CmsSite.objects.get(pk=id)
    except CmsSite.DoesNotExist:
        # Create CmsSite object on demand, populate with existing site values
        # so nothing is overwritten with empty values
        site = Site.objects.get_current()
        wrapper = CmsSite(**model_to_dict(site))
        wrapper.save()
        return wrapper


# -------- Models --------


class CmsSite(Site):
    """
    A CmsSite holds all global settings for a site
    """

    class Meta:
        verbose_name = _('CMS Site')
        verbose_name_plural = _('CMS Sites')


class CmsObject(MPTTModel):
    """
    A ```CmsObject``` represents one tree node (e.g. HTML page) of the site.
    """

    # Some publication states
    DRAFT = 'd'
    PUBLISHED = 'p'
    EXPIRED = 'e'
    HIDDEN = 'h'
    STATUSES = (
        (PUBLISHED, _('Published')),
        (HIDDEN, _('Hidden')),
        (DRAFT, _('Draft')),
    )

    # Some content types

    # Standard metadata
    title = models.CharField(max_length=255)
    slug = models.SlugField(validators=[validate_slug], help_text=_("The slug is used in the URL of the page"))
    parent = models.ForeignKey('self', blank=True, null=True, editable=False, related_name=_('children'), verbose_name=_('parent'))
    parent_site = models.ForeignKey(CmsSite, editable=False, default=_get_current_site)

    # SEO fields, misc
    keywords = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    sort_order = models.IntegerField(editable=False, default=0)

    # Publication information
    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT)
    publication_date = models.DateTimeField(_('publication date'), null=True, blank=True, help_text=_('''When the page should go live, status must be "Published".'''))
    expire_date = models.DateTimeField(_('publication end date'), null=True, blank=True)

    # Metadata
    author = models.ForeignKey(User, verbose_name=_('author'), editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

    # Django settings
    objects = CmsObjectManager()

    class Meta:
        ordering = ('lft', 'sort_order', 'title')
        verbose_name = _('Object node')
        verbose_name_plural = _('Object nodes')

    class MPTTMeta:
        order_insertion_by = 'title'

    def __unicode__(self):
        return self.title


class CmsPageItem(models.Model):
    """
    A ```PageItem``` is a content part which is displayed at the page.
    """
    parent = models.ForeignKey(CmsObject)
    sort_order = models.IntegerField(editable=False)
    region = models.CharField(max_length=128)

    class Meta:
        ordering = ('parent', 'sort_order')
        verbose_name = _('Page Item')
        verbose_name_plural = _('Page Items')


# -------- Legacy mptt support --------

if hasattr(mptt, 'register'):
    # MPTT 0.3 legacy support
    mptt.register(CmsObject)