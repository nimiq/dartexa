from __future__ import unicode_literals

from django.db import models


class Dart(models.Model):
    score = models.IntegerField()
    multiplier = models.IntegerField()

    def __unicode__(self):
        return '{}|{}|{}'.format(self.id, self.score, self.multiplier)


class Player(models.Model):
    name = models.CharField(max_length=128)
    score = models.IntegerField(default=51)

    def __unicode__(self):
        return '{}|{}'.format(self.name, self.score)


class Game(models.Model):
    STATUS_CHOICES = (
        ('r', 'running'),
        ('f', 'finished'),
        ('c', 'cancelled')
    )
    target = models.IntegerField(default=51)
    status = models.CharField(choices=STATUS_CHOICES, default='r', max_length=1)

    def __unicode__(self):
        return '{}|{}'.format(self.id, self.status)


class Turn(models.Model):
    STATUS_CHOICES = (
        ('p', 'pending'),
        ('d', 'done'),
        ('v', 'void')
    )

    dart1 = models.ForeignKey(Dart, related_name='turn1', blank=True, null=True)
    dart2 = models.ForeignKey(Dart, related_name='turn2', blank=True, null=True)
    dart3 = models.ForeignKey(Dart, related_name='turn3', blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default='p', max_length=1)
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)

    def __unicode__(self):
        return '{}|{}'.format(self.id, self.status)