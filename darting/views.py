from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework import viewsets, views, response
from .models import *


def index(request):
    return HttpResponse("Paolo won!")


class TestViewSet(views.APIView):
    def get(self, request):
        say = request.query_params.get('q', 'test one two three')
        return response.Response({'say': say + '. GET.'})

    def post(self, request):
        say = request.data.get('q', 'test one two three')
        return response.Response({'say': say + '. POST.'})


class GameViewSet(views.APIView):
    def post(self, request):
        # Check for running games.
        if Game.objects.filter(status='r').exists():
            say = 'Error: there is already a running game.'
            return response.Response({'say': say})

        # Create new game.
        game = Game.objects.create()
        player1 = Player.objects.get(pk=1)
        player1.score = 501
        player1.save()
        player2 = Player.objects.get(pk=2)
        player2.score = 501
        player2.save()
        turn = Turn.objects.create(
            status='p',
            player=player1,
            game=game
        )

        say = 'Game {} started. {} to play first. {} to go.'.format(
            game.pk, player1.name, player1.score
        )
        return response.Response({'say': say})


class GameCancelViewSet(views.APIView):
    def post(self, request):
        # Get all the running game and cancel them.
        amt = Game.objects.filter(status='r').update(status='c')
        say = '{} game cancelled.'.format(amt)
        return response.Response({'say': say})


class DartViewSet(views.APIView):
    def post(self, request):
        # Input validation.
        score = request.data.get('score')
        multiplier = request.data.get('multiplier')
        if not score or not multiplier:
            say = 'Error: input invalid.'
            return response.Response({'say': say})

        # Get the running game.
        try:
            game = Game.objects.get(status='r')
        except Game.DoesNotExist:
            say = 'No running game. Create a game first.'
            return response.Response({'say': say})
        except Game.MultipleObjectsReturned:
            say = 'Multiple running games. Cancel the running games first.'
            return response.Response({'say': say})

        # Get the game's latest turn.
        turn = Turn.objects.filter(game=game).exclude(status='void').order_by('-id').first()

        # There is no turn yet.
        if not turn:
            turn = Turn.objects.create(
                status='p',
                player=Player.objects.get(pk=1),
                game=game
            )

        # If the turn is done: create a new turn for the other player.
        if turn.status == 'd':
            turn = Turn.objects.create(
                status='p',
                player=Player.objects.exclude(id=turn.player.id).first(),
                game=game
            )

        # If the turn is pending.
        # Create a dart.
        dart = Dart.objects.create(
            score=score,
            multiplier=multiplier,
        )

        # Add the dart to the pending turn.
            # darts123 = [turn.dart1, turn.dart2, turn.dart3]
            # empty_darts = list(filter(lambda x: not bool(x), darts123))
            # if not empty_darts:
            #     say = 'Error: corrupted turn.'
            #     return response.Response({'say': say})
            # empty_darts[0] = dart
            # turn.save()
        empty_dart_count = 0
        if not turn.dart1:
            empty_dart_count += 1
            turn.dart1 = dart
        elif not turn.dart2:
            empty_dart_count += 1
            turn.dart2 = dart
        elif not turn.dart3:
            empty_dart_count += 1
            turn.dart3 = dart
        turn.save()
        if not empty_dart_count:
            say = 'Error: corrupted turn.'
            return response.Response({'say': say})

        # If there is only 1 dart missing: close the turn.
        if empty_dart_count == 1:
            turn.status = 'd'
            turn.save()

        # Update player's score and check for victory.
        turn.player.score -= dart.score
        turn.player.save()

        # Check for victory.
        # If the player won.
        if turn.player.score == 0 and dart.multiplier == 2:
            turn.status = 'd'
            turn.save()
            game.status = 'f'
            game.save()
            say = '{} won the game!'.format(turn.player.name)
            return response.Response({'say': say})
        elif turn.player.score > 0:
            if turn.status == 'd':
                say = '{} to go for {}. Now {} to play.'.format(
                    turn.player.score, turn.player.name,
                    Player.objects.exclude(id=turn.player.id).first().name,
                )
                return response.Response({'say': say})
            elif turn.status == 'p':
                darts123 = [turn.dart1, turn.dart2, turn.dart3]
                empty_darts = list(filter(lambda x: not bool(x), darts123))
                say = '{} to go for {}. It will be your dart number {}.'.format(
                    turn.player.score, turn.player.name,
                    4-len(empty_darts),
                )
                return response.Response({'say': say})
        else:  # finish w/out a double or under zero.
            # Void the turn and update player score.
            turn.status = 'v'
            turn.save()

            total = 0
            for attr_name in ['dart1', 'dart2', 'dart3']:
                d = getattr(turn, attr_name)
                if d:
                    total += d.score
            turn.player.score += total
            turn.player.save()

            say = 'Too bad {}: you voided your turn! Now {} to play.'.format(
                turn.player.name,
                Player.objects.exclude(id=turn.player.id).first().name,
            )
            return response.Response({'say': say})


class DartCancelViewSet(views.APIView):
    def post(self, request):
        pass


