import string
import random

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

# Create your models here.


KEY_STATUS_NEW = 0
KEY_STATUS_ACQUIRED = 1
KEY_STATUS_ACTIVATED = 2

KEY_STATUS_CHOICES = (
    (KEY_STATUS_NEW, _("new")),
    (KEY_STATUS_ACQUIRED, _("acquired")),
    (KEY_STATUS_ACTIVATED, _("activated")),
)

KEY_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits
KEY_LENGTH = 4


def status2text(status):
    ''' Числовое значение статуса в название '''
    return dict(KEY_STATUS_CHOICES).get(status, None)

class KeysManager(models.Manager):
    @property
    def free(self):
        ''' Только невыданные ключи '''
        return self.get_queryset().filter(status=KEY_STATUS_NEW)

    @property
    def used(self):
        ''' Ключи, которые были выданы и, возможно, активированы '''
        return self.get_queryset().filter(status__ne=KEY_STATUS_NEW)

    @property
    def activated(self):
        ''' Только активированные ключи '''
        return self.get_queryset().filter(status=KEY_STATUS_ACTIVATED)

    @property
    def acquired(self):
        ''' Ключи, которые были выданы, но еще не использованы '''
        return self.get_queryset().filter(status=KEY_STATUS_ACQUIRED)


class Key(models.Model):
    symbols = models.CharField(max_length=KEY_LENGTH,
                              unique=True,
                              default=KEY_STATUS_NEW,
                              verbose_name=_("symbols"))
    status = models.SmallIntegerField(choices=KEY_STATUS_CHOICES,
                                      verbose_name=_("status"))

    objects = KeysManager()

    def acquire(self):
        ''' Выдать ключ. Если уже выдан, вернуть False иначе True '''
        if self.status == KEY_STATUS_NEW:
            self.status = KEY_STATUS_ACQUIRED
            self.save()
            return True
        else:
            return False

    def activate(self):
        '''
        Активировать ключ. Если еще не выдан или уже активирован,
        вернуть False, иначе True
        '''
        if self.status == KEY_STATUS_ACQUIRED:
            self.status = KEY_STATUS_ACTIVATED
            self.save()
            return True
        else:
            return False

    @property
    def is_activated(self):
        ''' Был ли ключ уже активирован '''
        return self.status == KEY_STATUS_ACTIVATED

    @property
    def verbose_status(self):
        ''' Название статуса словами '''
        return status2text(self.status)

    def __str__(self):
        return self.symbols

    @classmethod
    def gen_new(cls):
        ''' Генерировать новый ключ '''
        saved = False
        while not saved:
            key = cls(symbols=''.join(random.choices(KEY_ALPHABET,
                                                     k=KEY_LENGTH)),
                      status=KEY_STATUS_NEW)
            try:
                key.save()
                saved = True
            except IntegrityError:
                pass
        return key

    @classmethod
    def by_symbols(cls, symbols):
        ''' Найти ключ по его коду '''
        return cls.objects.filter(symbols=symbols).first()

    class Meta:
        permissions = (
            ('generate_key', _("Can generate keys")),
            ('get_key', _("Can get a key")),
            ('use_key', _("Can use a key")),
            ('check_key_status', _("Can check key status")),
            ('get_key_count', _("Can get key count")),
        )
        verbose_name = _("key")
        verbose_name_plural = _("keys")
