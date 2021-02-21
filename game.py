from random import shuffle
from typing import Set, Dict, Any, Tuple, Optional, Union
from enum import Enum

FACE_RANKS = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
FACE_SUITS = ["DIAMONDS", "CLUBS", "HEARTS", "SPADES"]

class Card:
    def __init__(self, value: int):
        if not 0 <= value < 52:
            raise ValueError(f"Cannot build Card from value: {value}")
        self.value = value
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

    def serialize(self) -> Dict[str, Union[str, int]]:
        return { "value": self.value, "rank": self.rank, "suit": self.suit }

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

class Game:
    def __init__(self, player_ids: list[str]):
        self.player_ids = player_ids
        self.player_status = [PlayerStatus.ACTIVE] * len(player_ids)
        self.card_stack: list[Card] = []
        self.player_hands = deal_hands(len(player_ids))
        self.current_player_no = self.starting_player_no()
        self.last_card_played_player_no = -1

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
            "hand": list(c.serialize() for c in sorted(hand, key=lambda c: c.rank)),
            "top_card": self.card_stack[-1].serialize() if self.card_stack else None,
            "playable_cards": list(c.serialize() for c in sorted(playable_cards(self.card_stack, hand), key=lambda c: c.rank)),
            "game_finished": self.is_game_finished(),
        }

    def is_game_finished(self) -> bool:
        return all(sts == PlayerStatus.FINISHED for sts in self.player_status)

    def play_turn(self, player_no: int, move: Move, card: Card) -> Tuple[TurnResult, list[TurnEvent]]:
        events: list[TurnEvent] = []
        if player_no != self.current_player_no:
            return TurnResult.WRONG_PLAYER, events

        if self.player_status == PlayerStatus.PASSED:
            return TurnResult.PLAYER_PASSED, events

        if self.player_status == PlayerStatus.FINISHED:
            return TurnResult.PLAYER_FINISHED, events

        if move == Move.PASS:
            self.player_status[player_no] = PlayerStatus.PASSED
            events.append(TurnEvent.PLAYER_PASSED)
            next_turn_events = self.prepare_next_turn()
            events.extend(next_turn_events)
            return TurnResult.SUCCESS, events

        # Player has chosen to play a card
        hand = self.player_hands[player_no]

        if card not in hand:
            return TurnResult.CARD_NOT_IN_HAND, events

        if card not in playable_cards(self.card_stack, hand):
            return TurnResult.CARD_NOT_PLAYABLE, events

        hand.remove(card)
        self.card_stack.append(card)
        self.last_card_played_player_no = self.current_player_no

        if len(hand) == 0:
            self.player_status[player_no] = PlayerStatus.FINISHED
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
        for player_no in range_wrapped(len(self.player_ids), offset=self.current_player_no + 1):
            if player_no == self.last_card_played_player_no:
                # Passes all round, back to the last card player
                events = [TurnEvent.ROUND_FINISHED]
                if self.player_status[player_no] == PlayerStatus.FINISHED:
                    next_player_no = self.find_first_non_finished_player_no(start_no=player_no + 1)
                    if next_player_no is None:
                        events.append(TurnEvent.GAME_FINISHED)
                        return -1, events
                    else:
                        return next_player_no, events
                else:
                    return player_no, events
            elif self.player_status[player_no] == PlayerStatus.ACTIVE:
                return player_no, []
        assert False

    def find_first_non_finished_player_no(self, start_no) -> Optional[int]:
        try:
            return next(
                p_no
                for p_no in range_wrapped(len(self.player_ids), offset=start_no)
                if self.player_status[p_no] != PlayerStatus.FINISHED
            )
        except StopIteration:
            return None

    def reset_round(self):
        self.card_stack = []
        for player_no in range(len(self.player_ids)):
            if self.player_status[player_no] == PlayerStatus.PASSED:
                self.player_status[player_no] = PlayerStatus.ACTIVE


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
