from enum import Enum
from typing import NamedTuple, Optional

from sqlalchemy.orm.attributes import flag_modified # type: ignore

from models import Game, Player
from models.player import PlayerStatus
import card as Card

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

def play_turn(game: Game, player: Player, move: Move, card: int) -> tuple[TurnResult, list[TurnEvent]]:
    events: list[TurnEvent] = []
    if player.game_player_index != game.current_player_index:
        return TurnResult.WRONG_PLAYER, events
    if player.status == PlayerStatus.PASSED:
        return TurnResult.PLAYER_PASSED, events
    if player.status == PlayerStatus.FINISHED:
        return TurnResult.PLAYER_FINISHED, events

    if move == Move.PASS:
        player.status = PlayerStatus.PASSED
        events.append(TurnEvent.PLAYER_PASSED)
        next_turn_events = prepare_next_turn(game)
        events.extend(next_turn_events)
        return TurnResult.SUCCESS, events

    # Player has chosen to play a card
    if card not in player.hand:
        return TurnResult.CARD_NOT_IN_HAND, events
    if card not in playable_cards(game.last_card, player.hand):
        return TurnResult.CARD_NOT_PLAYABLE, events

    player.hand.remove(card)
    # The reference has not changed, so we need to explicitly update
    flag_modified(player, "hand")

    game.last_card = card
    game.last_card_player_index = game.current_player_index

    if len(player.hand) == 0:
        player.status = PlayerStatus.FINISHED
        events.append(TurnEvent.PLAYER_FINISHED)

    next_turn_events = prepare_next_turn(game)
    events.extend(next_turn_events)
    return TurnResult.SUCCESS, events

def prepare_next_turn(game: Game) -> list[TurnEvent]:
    next_player_index, events = find_next_player_no(game)
    if next_player_index == -1:
        # Game has finished
        return events
    elif TurnEvent.ROUND_FINISHED in events:
        reset_round(game)
    game.current_player_index = next_player_index
    game.turn_number += 1
    return events

def find_next_player_no(game: Game) -> tuple[int, list[TurnEvent]]:
    """
    Assumes that `self.current_player_index` has just finished their turn.
    """
    # Iterate through players, starting with the person right after the current player
    players = Player.query.filter_by(game_id=game.id).order_by(Player.game_player_index).all()
    for player_index in range_wrapped(len(players), offset=game.current_player_index + 1):
        player = players[player_index]
        if player_index == game.last_card_player_index:
            # Passes all round, back to the last card player
            events = [TurnEvent.ROUND_FINISHED]
            if player.status == PlayerStatus.FINISHED:
                next_player_index = find_first_non_finished_player_index(players, start_index=player_index + 1)
                if next_player_index is None:
                    events.append(TurnEvent.GAME_FINISHED)
                    return -1, events
                else:
                    return next_player_index, events
            else:
                return player_index, events
        elif player.status == PlayerStatus.ACTIVE:
            return player_index, []
    assert False

def find_first_non_finished_player_index(players: list[Player], start_index: int) -> Optional[int]:
    try:
        return next(
            p_index
            for p_index in range_wrapped(len(players), offset=start_index)
            if players[p_index].status != PlayerStatus.FINISHED
        )
    except StopIteration:
        return None

def reset_round(game: Game):
    game.last_card = None
    for player in game.players:
        if player.status == PlayerStatus.PASSED:
            player.status = PlayerStatus.ACTIVE

def playable_cards(last_card: Optional[int], hand: list[int]) -> list[int]:
    if last_card:
        return [card for card in hand if Card.rank(card) >= Card.rank(last_card)]
    else:
        return [card for card in hand]

def range_wrapped(n, offset):
    """
    >>> list(range_wrapped(5, offset=2))
    [2, 3, 4, 0, 1]
    """
    for i in range(0, n):
        yield (i + offset) % n
