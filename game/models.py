import secrets, random, json, string
from django.db import models, transaction
from django.contrib.auth.models import User

SUITS = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
RANKS = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

class CardManager(models.Manager):
    def create(self, card, hidden=False):
        return super().create(suit=card['suit'], rank=card['rank'], hidden=hidden)

class Card(models.Model):
    SUIT_CHOICES = (
        ('H', 'Hearts'),
        ('D', 'Diamonds'),
        ('C', 'Clubs'),
        ('S', 'Spades'),
    )

    RANK_CHOICES = (
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('J', 'Jack'),
        ('Q', 'Queen'),
        ('K', 'King'),
        ('A', 'Ace'),
    )

    suit = models.CharField(max_length=1, choices=SUIT_CHOICES)
    rank = models.CharField(max_length=2, choices=RANK_CHOICES)
    hidden = models.BooleanField(default=False)

    objects = CardManager()

    def __str__(self):
        return f"{self.rank} of {self.suit}"
    

# Create your models here.
class Game(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_games')
    join_code = models.CharField(max_length=6, unique=True)
    players = models.ManyToManyField(User, related_name='games_joined')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_bet = models.IntegerField(default=1)
    max_bet = models.IntegerField(null=True)
    started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    hands = models.ManyToManyField('Hand', related_name='hands', blank=True)
    deck = models.TextField(blank=True)

    def __str__(self):
        return f"Game {self.join_code}"
    
    def save(self, *args, **kwargs):
        if not self.join_code:
            # Generate a unique 6-character join code
            while True:
                join_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6)).upper()
                if not Game.objects.filter(join_code=join_code).exists():
                    self.join_code = join_code
                    break
        super().save(*args, **kwargs)

    def start_game(self):
        self.create_deck()

        # Create hand for dealer
        self.create_hand(None)

        # Create hands for players
        for player in self.players.all():
            self.create_hand(player)
        
        self.started = True
        self.save()

    def create_hand(self, owner):
        hand = Hand.objects.create(game=self, user=owner, is_dealer=not owner)

        for i in range(2):
            card = self.draw_card()
            hand.add_card(Card.objects.create(card, hidden=not owner and i == 0))

        self.hands.add(hand)

    def create_deck(self):
        deck = []
        for _ in range(4):
            deck += self.create_single_deck()

        # shuffle deck
        random.shuffle(deck)

        # save deck state to database
        self.deck = json.dumps(deck)
        self.save()

    def create_single_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = []

        for suit in suits:
            for rank in ranks:
                card = {
                    'rank': rank,
                    'suit': suit
                }
                deck.append(card)

        return deck
    
    def draw_card(self):
        # load deck from database
        deck = json.loads(self.deck)

        # check if deck is empty
        if not deck:
            self.create_deck()
            deck = json.loads(self.deck)

        # draw card
        card = deck.pop()

        # save updated deck state to database
        self.deck = json.dumps(deck)
        self.save()

        return card

    def hit(self, player):
        hand = self.hands.get(game=self, user=player)
        if not hand.is_bust:
            card = self.draw_card()
            hand.add_card(Card.objects.create(card))

        return hand
    
    def stand(self, player):
        hand = self.hands.get(game=self, user=player)

        hand.stand = True
        hand.save()

        return hand
    
    def play_dealer(self):
        hand = self.hands.first()

        hidden_card = hand.cards.filter(hidden=True).first()

        hidden_card.hidden = False

        hidden_card.save()

        hand.current_total = hand.calculate_hand_value()

        if hand.current_total > 21: hand.is_bust = True

        hand.save()
        
        while hand.calculate_hand_value() < 17:
            card = self.draw_card()
            hand.add_card(Card.objects.create(card))
            hand.save()

        # Determine payout

        for player_hand in self.hands.filter(user__isnull=False):
            if not player_hand.is_bust and player_hand.current_total > hand.current_total:
                payout = player_hand.bet_amount * 2

                user_balance = player_hand.user.balance

                user_balance.balance = payout

                with transaction.atomic():
                    user_balance.save()

    def get_current_user_turn(self):
        # Get all hands in the game
        hands = self.hands.all()

        # Check if any hands are still active (have not bust and not stood)
        active_hands = [hand for hand in hands if not hand.is_bust and not hand.stand and not hand.is_dealer]

        # If there are active hands, return the first one in the list
        if active_hands:
            return active_hands[0].user

        # If there are no active or bust hands, return None
        return None

class Hand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_hands')
    cards = models.ManyToManyField(Card, blank=True)
    is_dealer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    bet_amount = models.PositiveIntegerField(default=0)
    chips = models.PositiveIntegerField(default=0)
    is_bust = models.BooleanField(default=False)
    stand = models.BooleanField(default=False)
    current_total = models.IntegerField(default=0)

    def __str__(self):
        if self.user:
            return f"{self.user.username}: {self.current_total} {'(Bust)' if self.is_bust else ''}{'(Stand)' if self.stand else ''}"
        else:
            return f"Dealer: {self.current_total} {'(Bust)' if self.is_bust else ''}"
    
    def add_card(self, card):
        self.cards.add(card)
        if not card.hidden:
            self.current_total = self.calculate_hand_value()
            if self.current_total > 21: 
                self.is_bust = True
                self.is_active = False
        self.save()

    def calculate_hand_value(self):
        """
        Calculates the total value of a hand.
        """
        total = 0
        num_aces = 0
        
        for card in self.cards.all():
            if card.hidden: continue
            if card.rank == 'A':
                num_aces += 1
            elif card.rank in ['K', 'Q', 'J']:
                total += 10
            else:
                total += int(card.rank)
        
        for i in range(num_aces):
            if total + 11 <= 21:
                total += 11
            else:
                total += 1

        return total