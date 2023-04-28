from django.shortcuts import render, redirect, get_object_or_404
from .models import Game
from .forms import NewGameForm, JoinGameForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from websocket import create_connection
import json


# send a websocket message to all players in the game
def send_message(join_code, action):
    ws = create_connection("ws://localhost:8000/ws/game/{join_code}/".format(join_code=join_code))
    message = {
        'type': 'action',
        'action': action,
    }

    ws.send(json.dumps(message))

    ws.close()

@login_required
def play(request, join_code):
    game = get_object_or_404(Game, join_code=join_code)

    user = game.get_current_user_turn()
    # render the game view with the game object
    return render(request, 'game/play.html', {'game': game, 'user_turn': user})

@login_required
def start_game(request, join_code):
    game = get_object_or_404(Game, join_code=join_code)

    if game.creator != request.user:
        messages.error(request, 'Only the game creator can start the game.')
        return redirect('play', join_code=join_code)

    if game.started:
        messages.error(request, 'The game has already started.')
        return redirect('play', join_code=join_code)
    
    game.start_game()

    send_message(join_code, 'start')

    # Redirect to the play page
    return redirect('game:play', join_code=join_code)

@login_required
def new(request):
    if request.method == 'POST':
        form = NewGameForm(request.POST)
        if form.is_valid():
            min_bet = form.cleaned_data['min_bet']
            max_bet = form.cleaned_data['max_bet']

            if min_bet <= 0:
                messages.error(request, 'Minimum bet must be greater than zero.')
                return render(request, 'game/new.html', {'form': form})
            if max_bet is not None and max_bet <= min_bet:
                messages.error(request, 'Maximum bet must be greater than the minimum bet.')
                return render(request, 'game/new.html', {'form': form})
            
            game = form.save(commit=False)
            game.creator = request.user
            game.save()
            game.players.add(request.user)

            return redirect('game:play', join_code=game.join_code)
    else:
        form = NewGameForm()
    return render(request, 'game/new.html', {'form': form})

@login_required
def join(request):
    if request.method == 'POST':
        form = JoinGameForm(request.POST)
        if form.is_valid():
            join_code = form.cleaned_data['joincode'].upper()
            try:
                game = Game.objects.get(join_code=join_code)
                if game.started:
                   messages.error(request, 'Game has already started')
                else:
                    game.players.add(request.user)
                    return redirect('game:play', join_code=game.join_code)

            except Game.DoesNotExist:
                 messages.error(request, 'Game not found')
            
            return render(request, 'game/join.html', {'form': form})
        else:
            print("HELLO WORLD")
    else:
        form = JoinGameForm()
    return render(request, 'game/join.html', {'form': form})

def hit(request, join_code):
    # get the game and user objects
    game = get_object_or_404(Game, join_code=join_code)
    user = request.user
    
    # get the hand for the user
    last_hand = game.hit(user)

    user_turn = game.get_current_user_turn()

    if not user_turn:
        # dealer turn
        game.play_dealer()
        send_message(join_code, 'dealer')
    else:
        # send a websocket message to all players
        send_message(join_code, 'hit')
    
    # check if the hand is bust
    return render(request, 'game/play.html', {'game': game, 'user_turn': user_turn, 'last_hand': last_hand})

def stand(request, join_code):
    # get the game and user objects
    game = get_object_or_404(Game, join_code=join_code)
    user = request.user

    game.stand(user)

    user_turn = game.get_current_user_turn()

    if not user_turn:
        # dealer turn
        game.play_dealer()
        send_message(join_code, 'dealer')
    else:
        # send a websocket message to all players
        send_message(join_code, 'stand')

    return render(request, 'game/play.html', {'game': game, 'user_turn': user_turn})
    
    # # reveal the dealer's hidden card
    # dealer_hand = game.hands.get(is_dealer=True)
    # dealer_card = dealer_hand.cards.filter(hidden=True).first()
    # dealer_card.hidden = False
    # dealer_card.save()
    
    # # deal cards to the dealer until their hand is at least 17
    # while dealer_hand.get_value() < 17:
    #     card = game.deck.deal_card()
    #     dealer_hand.cards.add(card)
    #     dealer_hand.save()
    
    # # determine the winner and update scores
    # winner = game.determine_winner()
    # game.update_scores(winner)
    # game.save()
    
    # # redirect to the results page
    # return redirect('game:results', join_code=join_code)