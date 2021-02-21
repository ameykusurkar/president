from pprint import pprint
import os

from game import Game, Move, Card, TurnResult, TurnEvent

def get_choice(num_options) -> int:
    choice = None
    while choice is None:
        cand = input("Pick an index to play: ")
        try:
            value = int(cand)
            if not 0 <= value < num_options:
                print(f"Invalid index: {value}. Try again.")
                continue
            choice = value
        except ValueError:
            print(f"Invalid value: {cand}, try again.")
            continue
    return choice

player_ids = [
    "amey",
    "batman",
    "superman",
    "spiderman",
    "quicksilver",
    "captain marvel",
]
game = Game(player_ids)
game_over = False

os.system("clear")
print("\n\n\n\n")
while not game_over:
    details = game.turn_details()

    max_length = max(len(s) for s in player_ids)
    for player in game.players:
        name = f"{player.id}:".ljust(max_length + 1)
        arrow = "   <-- to play" if details["player_id"] == player.id else ""
        status = str(player.status).split(".")[1]
        print(f"{name} {status}{arrow}")

    print()
    current_player_id = details['player_id']

    print(f"It is {current_player_id}'s turn.")
    print(f"Last card played: {details['top_card']}\n")
    print("These are the cards you have:")
    
    print(f"\t0: PASS")
    cards = details["hand"]
    for i, card in enumerate(cards, start=1):
        playable = "   <-- playable" if card in details["playable_cards"] else ""
        print(f"\t{i}: {str(card).ljust(15)}{playable}")

    print()
    choice = get_choice(num_options=len(cards)+1)

    os.system("clear")

    if choice == 0:
        # Doesn't matter what card we pass
        result, events = game.play_turn(details["player_no"], Move.PASS, Card(0))
        print(f"{current_player_id} passed.\n")
    else:
        card = cards[choice - 1]
        result, events = game.play_turn(details["player_no"], Move.PLAY, Card(card["value"]))
        print(f"{current_player_id} played {card}.\n")

    print(f"{result =}")
    print(f"{events =}")
    print()

    if TurnEvent.GAME_FINISHED in events:
        print("Game over!")
        game_over = True
