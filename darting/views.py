from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework import viewsets, views, response
from .models import *


class TestViewSet(views.APIView):
    def get(self, request):
        say = request.query_params.get('q', 'test one two three')
        print('Content: ' + say)
        return response.Response({'say': say + '. GET.'})

    def post(self, request):
        say = request.data.get('q', 'test one two three')
        print('Content: ' + say)
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
        player1.score = game.target
        player1.save()
        player2 = Player.objects.get(pk=2)
        player2.score = game.target
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
        if not amt:
            say = 'There is no running game, idiot!'.format(amt)
            return response.Response({'say': say})
        say = '{} game cancelled.'.format(amt)
        return response.Response({'say': say})


class DartViewSet(views.APIView):
    def post(self, request):
        # Input validation.
        score = request.data.get('score')
        multiplier = request.data.get('multiplier')
        print('Content score: ' + score)
        print('Content multiplier: ' + multiplier)

        if not score or not multiplier:
            say = 'Error: input invalid.'
            return response.Response({'say': say})

        try:
            score = int(score)
            multiplier = int(multiplier)
        except Exception:
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
        # turn = Turn.objects.filter(game=game).exclude(status='v').order_by('-id').first()
        turn = Turn.objects.filter(game=game).order_by('-id').first()

        # There is no turn yet.
        if not turn:
            turn = Turn.objects.create(
                status='p',
                player=Player.objects.get(pk=1),
                game=game
            )

        # If the turn is done: create a new turn for the other player.
        if turn.status == 'd' or turn.status == 'v':
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

        # Count empties.
        empty_dart_count = 0
        if not turn.dart1:
            empty_dart_count += 1
        if not turn.dart2:
            empty_dart_count += 1
        if not turn.dart3:
            empty_dart_count += 1

        # Add the dart to the pending turn.
        if not turn.dart1:
            turn.dart1 = dart
        elif not turn.dart2:
            turn.dart2 = dart
        elif not turn.dart3:
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
        elif turn.player.score > 1:
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
        # Get the running game.
        try:
            game = Game.objects.get(status='r')
        except Game.DoesNotExist:
            say = 'No running game. Create a game first.'
            return response.Response({'say': say})
        except Game.MultipleObjectsReturned:
            say = 'Multiple running games. Cancel the running games first.'
            return response.Response({'say': say})

        turn = Turn.objects.filter(game=game).order_by('-id').first()
        if turn.dart3:
            orig_dart_score = turn.dart3.score
            turn.dart3.delete()
            turn.dart3 = None

            if turn.status == 'v':
                turn.player.score -= (turn.dart1.score+turn.dart2.score)
                turn.player.save()
            elif turn.status == 'p' or turn.status == 'd':
                turn.player.score += orig_dart_score
                turn.player.save()

            turn.status = 'p'
            turn.save()

        elif turn.dart2:
            orig_dart_score = turn.dart2.score
            turn.dart2.delete()
            turn.dart2 = None

            if turn.status == 'v':
                turn.player.score -= turn.dart1.score
                turn.player.save()
            elif turn.status == 'p':
                turn.player.score += orig_dart_score
                turn.player.save()

            turn.status = 'p'
            turn.save()

        elif turn.dart1:
            orig_dart_score = turn.dart1.score
            turn.dart1.delete()
            turn.dart1 = None

            if turn.status == 'p':
                turn.player.score += orig_dart_score
                turn.player.save()

            turn.status = 'p'
            turn.save()

        else:
            say = 'Error: player {} has no dart yet.'.format(
                turn.player.name
            )
            return response.Response({'say': say})

        say = 'Score {} deleted for player {}.'.format(
            orig_dart_score, turn.player.name
        )
        return response.Response({'say': say})


class StatusViewSet(views.APIView):
    def get(self, request):
        # Get the running game.
        try:
            game = Game.objects.get(status='r')
        except Game.DoesNotExist:
            say = 'No running game. Create a game first.'
            return response.Response({'say': say})
        except Game.MultipleObjectsReturned:
            say = 'Multiple running games. Cancel the running games first.'
            return response.Response({'say': say})

        turn = Turn.objects.filter(game=game).order_by('-id').first()

        if turn.status == 'v' or turn.status == 'd':
            next_player = Player.objects.exclude(id=turn.player.id).first()
        else:
            next_player = turn.player

        dart_number = 1
        if not turn.dart1:
            dart_number = 1
        elif not turn.dart2:
            dart_number = 2
        elif not turn.dart3:
            dart_number = 3

        player1 = Player.objects.get(id=1)
        player2 = Player.objects.get(id=2)
        say = '{}: {} to go. {}: {} to go. {} to play his dart number {}.'.format(
            player1.name, player1.score,
            player2.name, player2.score,
            next_player.name, dart_number

        )
        return response.Response({'say': say})


def multiplier_to_string(multiplier):
    if multiplier == 1:
        return 'single'
    if multiplier == 2:
        return 'double'
    if multiplier == 3:
        return 'triple'


def get_status_frontend():
    # Info for the frontend.
    try:
        game = Game.objects.get(status='r')
    except Game.DoesNotExist:
        error = 'No running game. Create a game first.'
        return None
    except Game.MultipleObjectsReturned:
        error = 'Multiple running games. Cancel the running games first.'
        return None

    turn = Turn.objects.filter(game=game).order_by('-id').first()
    if not turn:
        error = 'No turn yet.'
        return None

    if turn.status == 'v' or turn.status == 'd':
        next_player = Player.objects.exclude(id=turn.player.id).first()
    else:
        next_player = turn.player

    first_player = Turn.objects.filter(game=game).order_by('id').first().player
    paolo = Player.objects.get(id=1)
    rodrigo = Player.objects.get(id=2)

    turns = Turn.objects.filter(game=game).order_by('id')
    rounds = []
    for _ in range(10):
        rounds.append(
            {
                "paolo": [
                    {"score": '-', "multiplier": '-'},
                    {"score": '-', "multiplier": '-'},
                    {"score": '-', "multiplier": '-'},
                ],
                "rodrigo": [
                    {"score": '-', "multiplier": '-'},
                    {"score": '-', "multiplier": '-'},
                    {"score": '-', "multiplier": '-'},
                ]
            }

        )

    i = 0
    j = 0
    while j < 10:
        # Read paolo.
        try:
            turn = turns[i]
        except IndexError:
            break

        rounds[j]['paolo'] = [
                {"score": str(turn.dart1.score) if turn.dart1 and turn.status!='v' else '-',
                 "multiplier": multiplier_to_string(turn.dart1.multiplier) if turn.dart1 else '-'},
                {"score": str(turn.dart2.score) if turn.dart2 and turn.status!='v' else '-',
                 "multiplier": multiplier_to_string(turn.dart2.multiplier) if turn.dart2 else '-'},
                {"score": str(turn.dart3.score) if turn.dart3 and turn.status!='v' else '-',
                 "multiplier": multiplier_to_string(turn.dart3.multiplier) if turn.dart3 else '-'},

            ]

        # Read Rodrigo.
        try:
            turn = turns[i+1]
        except IndexError:
            break

        rounds[j]["rodrigo"] = [
                {"score": str(turn.dart1.score) if turn.dart1 and turn.status!='v' else '-',
                 "multiplier": multiplier_to_string(turn.dart1.multiplier) if turn.dart1 else '-'},
                {"score": str(turn.dart2.score) if turn.dart2 and turn.status!='v' else '-',
                 "multiplier": multiplier_to_string(turn.dart2.multiplier) if turn.dart2 else '-'},
                {"score": str(turn.dart3.score) if turn.dart3 and turn.status!='v' else '-',
                 "multiplier": multiplier_to_string(turn.dart3.multiplier) if turn.dart3 else '-'},

            ]

        i += 2
        j += 1


    data = {
        "next_player": next_player.name.lower(),
        "first_player": first_player.name.lower(),
        "paolo_score": paolo.score,
        "rodrigo_score": rodrigo.score,
        "round0": rounds[0],
        "round1": rounds[1],
        "round2": rounds[2],
        "round3": rounds[3],
        "round4": rounds[4],
        "round5": rounds[5],
        "round6": rounds[6],
        "round7": rounds[7],
        "round8": rounds[8],
        "round9": rounds[9],
    }
    return data


def ui(request):
    return render(
        request, 'index.html', {'data': get_status_frontend()})


def ui_paolo(request):
    return render(request, 'stats-paolo.html')


def ui_rodrigo(request):
    return render(request, 'stats-rodrigo.html')
