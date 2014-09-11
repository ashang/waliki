# -*- coding: utf-8 -*-
import os.path
from django.db import models
import markups
from waliki import settings


class Page(models.Model):
    MARKUP_CHOICES = [(m.name, m.name) for m in markups.get_all_markups()]
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    path = models.CharField(max_length=200, unique=True)
    markup = models.CharField(max_length=20, choices=MARKUP_CHOICES, default=settings.WALIKI_DEFAULT_MARKUP)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.path

    def save(self, *args, **kwargs):
        self.slug = self.slug.strip('/')
        if not self.path:
            self.path = self.slug + self._markup_class.file_extensions[0]
        super(Page, self).save(*args, **kwargs)

    @property
    def raw(self):
        filename = os.path.join(settings.WALIKI_DATA_DIR, self.path)
        if not os.path.exists(filename):
            self.raw = ""
            return ""
        return open(filename, "r").read()

    @raw.setter
    def raw(self, value):
        filename = os.path.join(settings.WALIKI_DATA_DIR, self.path)
        try:
            os.makedirs(os.path.dirname(filename))
        except FileExistsError:
            pass
        with open(filename, "w") as f:
            f.write(value)

    @property
    def _markup(self):
        markup_settings = settings.WALIKI_MARKUPS_SETTINGS.get(self.markup, None)
        return self._markup_class(settings_overrides=markup_settings)

    @property
    def _markup_class(self):
        return markups.find_markup_class_by_name(self.markup)

    def _get_part(self, part):
        return getattr(self._markup, part)(self.raw)


    @property
    def body(self):
        return self._get_part('get_document_body')

    @property
    def stylesheet(self):
        return self._get_part('get_stylesheet')

    @property
    def javascript(self):
        return self._get_part('get_javascript')

