from __future__ import unicode_literals

from django.db import models


class Dart(models.Model):
    score = models.IntegerField()
    multiplier = models.IntegerField()


class Player(models.Model):
    name = models.CharField(max_length=128)
    score = models.IntegerField(default=501)


class Game(models.Model):
    STATUS_CHOICES = (
        ('r', 'running'),
        ('f', 'finished'),
        ('c', 'cancelled')
    )
    target = models.IntegerField(default=501)
    status = models.CharField(choices=STATUS_CHOICES, default='r', max_length=1)


class Turn(models.Model):
    STATUS_CHOICES = (
        ('p', 'pending'),
        ('d', 'done'),
        ('v', 'void')
    )

    dart1 = models.ForeignKey(Dart, related_name='turn1')
    dart2 = models.ForeignKey(Dart, related_name='turn2')
    dart3 = models.ForeignKey(Dart, related_name='turn3')
    status = models.CharField(choices=STATUS_CHOICES, default='p', max_length=1)
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
