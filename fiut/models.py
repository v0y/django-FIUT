#!/usr/bin/env python
# encoding: utf-8

from django.db import models

from .helpers import slugify


class CreatedAtMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class NameMixin(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class SlugMixin(models.Model):
    slug = models.SlugField(null=True, blank=True, unique=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # create slug
        if not self.slug:
            self.slug = slugify(self.name)

        # run normal save
        return super(SlugMixin, self).save(*args, **kwargs)
