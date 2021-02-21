from random import shuffle
from typing import Set, Dict, Any, Tuple, Optional, Union
from enum import Enum

from serialize import serialize_iterable
from game.card import Card

class PlayerStatus(Enum):
    ACTIVE   = 0
    PASSED   = 1
    FINISHED = 2

class Move(Enum):
    PLAY = 0
    PASS = 1

class TurnResult(Enum):
    SUCCESS           = 0
    WRONG_PLAYER      = 1
    PLAYER_PASSED     = 2
    PLAYER_FINISHED   = 3
    CARD_NOT_IN_HAND  = 4
    CARD_NOT_PLAYABLE = 5

class TurnEvent(Enum):
    PLAYER_PASSED   = 0
    PLAYER_FINISHED = 1
    ROUND_FINISHED  = 2
    GAME_FINISHED   = 3

class Player:
    def __init__(self, player_id: str, hand: set[Card]):
        self.id = player_id
        self.hand = hand
        self.status = PlayerStatus.ACTIVE

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hand": serialize_iterable(sorted(self.hand, key=lambda c: c.rank)),
            "status": str(self.status),
        }

class Game:
    def __init__(self, player_ids: list[str]):
        hands = deal_hands(len(player_ids))
        self.players = list(Player(player_id, hand) for (player_id, hand) in zip(player_ids, hands))
        self.current_player_no = self.starting_player_no()
        self.card_stack: list[Card] = []
        self.last_card_played_player_no = -1

    def starting_player_no(self) -> int:
        """
        Player with 3 OF DIAMONDS starts
        """
        return next(i for i, p in enumerate(self.players) if Card(0) in p.hand)

    def turn_details(self) -> Dict[str, Any]:
        player = self.players[self.current_player_no]
        return {
            "player_no": self.current_player_no,
            "player_id": player.id,
            "hand": serialize_iterable(sorted(player.hand, key=lambda c: c.rank)),
            "top_card": self.card_stack[-1].serialize() if self.card_stack else None,
            "playable_cards": serialize_iterable(sorted(playable_cards(self.card_stack, player.hand), key=lambda c: c.rank)),
            "game_finished": self.is_game_finished(),
        }

    def serialize(self) -> Dict[str, Any]:
        player = self.players[self.current_player_no]
        return {
            "player_no": self.current_player_no,
            "player": player.serialize(),
            "top_card": self.card_stack[-1].serialize() if self.card_stack else None,
            "playable_cards": serialize_iterable(sorted(playable_cards(self.card_stack, player.hand), key=lambda c: c.rank)),
            "game_finished": self.is_game_finished(),
        }

    def is_game_finished(self) -> bool:
        return all(p.status == PlayerStatus.FINISHED for p in self.players)

    def play_turn(self, player_no: int, move: Move, card: Card) -> Tuple[TurnResult, list[TurnEvent]]:
        events: list[TurnEvent] = []
        if player_no != self.current_player_no:
            return TurnResult.WRONG_PLAYER, events

        player = self.players[player_no]

        if player.status == PlayerStatus.PASSED:
            return TurnResult.PLAYER_PASSED, events

        if player.status == PlayerStatus.FINISHED:
            return TurnResult.PLAYER_FINISHED, events

        if move == Move.PASS:
            player.status = PlayerStatus.PASSED
            events.append(TurnEvent.PLAYER_PASSED)
            next_turn_events = self.prepare_next_turn()
            events.extend(next_turn_events)
            return TurnResult.SUCCESS, events

        # Player has chosen to play a card
        if card not in player.hand:
            return TurnResult.CARD_NOT_IN_HAND, events

        if card not in playable_cards(self.card_stack, player.hand):
            return TurnResult.CARD_NOT_PLAYABLE, events

        player.hand.remove(card)
        self.card_stack.append(card)
        self.last_card_played_player_no = self.current_player_no

        if len(player.hand) == 0:
            player.status = PlayerStatus.FINISHED
            events.append(TurnEvent.PLAYER_FINISHED)

        next_turn_events = self.prepare_next_turn()
        events.extend(next_turn_events)
        return TurnResult.SUCCESS, events

    def prepare_next_turn(self) -> list[TurnEvent]:
        next_player_no, events = self.find_next_player_no()
        if next_player_no == -1:
            # Game has finished
            return events
        elif TurnEvent.ROUND_FINISHED in events:
            self.reset_round()
        self.current_player_no = next_player_no
        return events

    def find_next_player_no(self) -> Tuple[int, list[TurnEvent]]:
        """
        Assumes that `self.current_player_no` has just finished their turn.
        """
        # Iterate through players, starting with the person right after the current player
        for player_no in range_wrapped(len(self.players), offset=self.current_player_no + 1):
            player = self.players[player_no]
            if player_no == self.last_card_played_player_no:
                # Passes all round, back to the last card player
                events = [TurnEvent.ROUND_FINISHED]
                if player.status == PlayerStatus.FINISHED:
                    next_player_no = self.find_first_non_finished_player_no(start_no=player_no + 1)
                    if next_player_no is None:
                        events.append(TurnEvent.GAME_FINISHED)
                        return -1, events
                    else:
                        return next_player_no, events
                else:
                    return player_no, events
            elif player.status == PlayerStatus.ACTIVE:
                return player_no, []
        assert False

    def find_first_non_finished_player_no(self, start_no) -> Optional[int]:
        try:
            return next(
                p_no
                for p_no in range_wrapped(len(self.players), offset=start_no)
                if self.players[p_no].status != PlayerStatus.FINISHED
            )
        except StopIteration:
            return None

    def reset_round(self):
        self.card_stack = []
        for player in self.players:
            if player.status == PlayerStatus.PASSED:
                player.status = PlayerStatus.ACTIVE


def range_wrapped(n, offset):
    """
    >>> list(range_wrapped(5, offset=2))
    [2, 3, 4, 0, 1]
    """
    for i in range(0, n):
        yield (i + offset) % n

def playable_cards(card_stack: list[Card], hand: Set[Card]) -> Set[Card]:
    if card_stack:
        return set(card for card in hand if card.rank >= card_stack[-1].rank)
    else:
        return set(card for card in hand)

def deal_hands(n: int) -> list[Set[Card]]:
    deck = [Card(i) for i in range(52)]
    shuffle(deck)
    hands: list[Set[Card]] = [set() for _ in range(n)]
    counter = 0
    while deck:
      hands[counter].add(deck.pop())
      counter = (counter + 1) % n
    return hands
