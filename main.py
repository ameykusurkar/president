from functools import total_ordering
from random import shuffle
from typing import List, Set, Dict, Any, Tuple
from enum import Enum

FACE_RANKS = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
FACE_SUITS = ["DIAMONDS", "CLUBS", "HEARTS", "SPADES"]

class Card:
    def __init__(self, value: int):
        self.value = value % 52
        self.rank = self.value % 13
        self.suit = self.value // 13

    def __repr__(self):
        return f"Card({self.value})"

    def __str__(self):
        return f"{FACE_RANKS[self.rank]} OF {FACE_SUITS[self.suit]}"

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value

class PlayerStatus(Enum):
    ACTIVE   = 0
    PASSED   = 1
    FINISHED = 2

class Move(Enum):
    PLAY = 0
    PASS = 1

class TurnResult(Enum):
    SUCCESS          = 0
    WRONG_PLAYER     = 1
    PLAYER_PASSED    = 2
    PLAYER_FINISHED  = 3
    CARD_NOT_IN_HAND = 4
    INVALID_CARD     = 5

class TurnEvent(Enum):
    PLAYER_PASSED      = 0
    PLAYER_FINISHED    = 1
    ROUND_FINISHED     = 2
    GAME_FINISHED      = 3

class Game:
    def __init__(self, player_ids: List[str]):
        self.player_ids = player_ids
        self.player_status = [PlayerStatus.ACTIVE for _ in range(len(player_ids))]
        self.card_stack: List[Card] = []
        self.player_hands = deal_hands(len(player_ids))
        self.current_player_no = self.starting_player_no()

    def starting_player_no(self) -> int:
        """
        Player with 3 OF DIAMONDS starts
        """
        return next(p for p in range(len(self.player_ids)) if Card(0) in self.player_hands[p])

    def turn_details(self) -> Dict[str, Any]:
        hand = self.player_hands[self.current_player_no]
        return {
            "player_no": self.current_player_no,
            "player_id": self.player_ids[self.current_player_no],
            "hand": hand,
            "top_card": self.card_stack[-1] if self.card_stack else None,
            "playable_cards": playable_cards(self.card_stack, hand)
        }

    def play_turn(self, player_no: int, move: Move, card: Card) -> Tuple[TurnResult, List[TurnEvent]]:
        events: List[TurnEvent] = []
        if player_no != self.current_player_no:
            return TurnResult.WRONG_PLAYER, events

        if self.player_status == PlayerStatus.PASSED:
            return TurnResult.PLAYER_PASSED, events

        if self.player_status == PlayerStatus.FINISHED:
            return TurnResult.PLAYER_FINISHED, events

        if move == Move.PASS:
            self.player_status[player_no] = PlayerStatus.PASSED
            events.append(TurnEvent.PLAYER_PASSED)
            return TurnResult.SUCCESS, events

        # Player has chosen to play a card
        hand = self.player_hands[player_no]

        if card not in hand:
            return TurnResult.CARD_NOT_IN_HAND, events

        hand.remove(card)
        self.card_stack.append(card)

        if len(hand) == 0:
            self.player_status[player_no] = PlayerStatus.FINISHED
            events.append(TurnEvent.PLAYER_FINISHED)

        return TurnResult.SUCCESS, events

    # def next_player_no(self) -> int:
    #     """
    #     Assumes that `self.current_player_no` has just finished their turn.
    #     """
    #     for offset in range(1, len(self.player_ids)):
    #         player_no = (self.current_player_no + offset) % len(self.player_ids)
    #         if self.player_status[player_no] == PlayerStatus.ACTIVE:
    #             return player_no
    #     return -1


def playable_cards(card_stack: List[Card], hand: Set[Card]) -> Set[Card]:
    if card_stack:
        return set(card for card in hand if card.rank >= card_stack[-1].rank)
    else:
        return set(card for card in hand)

def deal_hands(n: int) -> List[Set[Card]]:
    deck = [Card(i) for i in range(52)]
    shuffle(deck)
    hands: List[Set[Card]] = [set() for _ in range(n)]
    counter = 0
    while deck:
      hands[counter].add(deck.pop())
      counter = (counter + 1) % n
    return hands
