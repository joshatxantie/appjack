# game/consumers.py
import json
from .models import Game
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.join_code = self.scope['url_route']['kwargs']['join_code']
        game = self.get_game(self.join_code)

        if not game:
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(
            self.join_code, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.join_code, self.channel_name
        )

    def receive(self, text_data):
        game = self.get_game(self.join_code)

        if not game:
            self.close()
            return

        message = json.loads(text_data)

        if message['type'] == 'player_joined':
            player = self.scope['user']

            if player:
                game.players.add(player)
                self.update_players_list(game)
        if message['type'] == 'action':
            self.send(text_data=json.dumps({
            'type': 'action',
            'action': message.get('action'),
        }))

    def update_players_list(self, game):
        all_players = game.players.all()
        players = [player.username for player in all_players]
        async_to_sync(self.channel_layer.group_send)(self.join_code, {
            'type': 'send_players_list',
            'players': players,
        })

    def send_players_list(self, event):
        players = event['players']
        self.send(text_data=json.dumps({
            'type': 'players_list',
            'players': players,
        }))

    def get_game(self, join_code):
        try:
            game = self.scope['game']
        except KeyError:
            try:
                game = Game.objects.get(join_code=join_code)
            except Game.DoesNotExist:
                return None

        self.scope['game'] = game
        return game
