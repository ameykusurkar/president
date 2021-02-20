from pprint import pprint
import os

from game import Game, Move, Card, TurnResult, TurnEvent

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
    for i, player_id in enumerate(player_ids):
        name = f"{player_id}:".ljust(max_length + 1)
        arrow = "   <-- to play" if details["player_no"] == i else ""
        status = str(game.player_status[i]).split(".")[1]
        print(f"{name} {status}{arrow}")

    print()
    current_player_id = details['player_id']

    print(f"It is {current_player_id}'s turn.")
    print(f"Last card played: {details['top_card']}\n")
    print("These are the cards you have:")
    
    print(f"\t0: PASS")
    cards = list(details["hand"])
    for i, card in enumerate(cards, start=1):
        print(f"\t{i}: {str(card)}")

    print()
    try:
        choice = int(input("Pick an index to play: "))
    except ValueError:
        continue

    os.system("clear")

    if choice == 0:
        # Doesn't matter what card we pass
        result, events = game.play_turn(details["player_no"], Move.PASS, Card(0))
        print(f"{current_player_id} passed.\n")
    else:
        card = cards[choice - 1]
        result, events = game.play_turn(details["player_no"], Move.PLAY, card)
        print(f"{current_player_id} played {card}.\n")

    print(f"{result =}")
    print(f"{events =}")
    print()

    if TurnEvent.GAME_FINISHED in events:
        game_over = True
