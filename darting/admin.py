from django.contrib import admin

from .models import *


@admin.register(Dart)
class DartAdmin(admin.ModelAdmin):
    """
    Simple audit logs belonging to the Toggle
    """
    list_display = ('pk', 'score', 'multiplier')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
    Simple audit logs belonging to the Toggle
    """
    list_display = ('pk', 'name', 'score')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Simple audit logs belonging to the Toggle
    """
    list_display = ('pk', 'target', 'status')


@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    """
    Simple audit logs belonging to the Toggle
    """
    list_display = ('pk', 'dart1', 'dart2', 'dart3', 'status', 'player', 'game')



