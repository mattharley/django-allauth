from datetime import datetime

from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from itertools import chain

class SocialAccountQuery(object):
    def __init__(self, models=None):
        self.models = models
        self.queries = list()
        for model in models:
            self.queries.append(model.objects.all())
        
    def __iter__(self):
        return chain(*(self.queries))
    
    def filter(self, *args, **kwargs):
        qs = self._clone()
        for query in qs.queries:
            query = query.filter(*args, **kwargs)
        return qs
    
    def _clone(self):
        qs = SocialAccountQuery(models=list(self.models))
        qs.queries = list()
        for query in self.queries:
            qs.queries.append(query._clone())
        return qs
    
class SocialAccountManager(object):
    def get_empty_query_set(self):
        return models.query.EmptyQuerySet()

    def get_query_set(self):
        return SocialAccountQuery(SocialAccount.__subclasses__())
    
    def none(self):
        return self.get_empty_query_set()
    
    def filter(self, *args, **kwargs):
        return self.get_query_set().filter(*args, **kwargs)

class SocialAccount(models.Model):
    objects = SocialAccountManager()
    
    user = models.ForeignKey(User)
    # No social_id here because I want it to be unique
    last_login = models.DateTimeField(default=datetime.now)
    date_joined = models.DateTimeField(default=datetime.now)
    
    def authenticate(self):
        return authenticate(account=self)


    def __unicode__(self):
        return unicode(self.user)
    
    def get_avatar_url(self):
        return None

    def get_provider(self):
        raise NotImplementedError

    def get_provider_account(self):
        for f in ['twitteraccount', 'openidaccount', 'facebookaccount']:
            try:
                return getattr(self, f)
            except self._meta.get_field_by_name(f)[0].model.DoesNotExist:
                pass
        assert False
        
    class Meta:
        abstract = True
