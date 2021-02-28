import React, { useState, useEffect } from "react";
import "./App.css";
import Card from "./Card";

// TODO: There's a bug when checking `game.current_player_id` to refresh state:
// there's a scenario where the game has progressed, but the current player has
// not changed.
function App() {
  const [game, setGame] = useState({ player_ids: [] });
  const [players, setPlayers] = useState([]);
  const [playerID, setPlayerID] = useState("");
  const [youPlayer, setYouPlayer] = useState({ hand: [] });

  useEffect(() => {
    const interval = setInterval(refreshGame, 2000);
    return () => {
      clearInterval(interval);
    };
  }, []);

  // TODO: Find a good fix for this. Because `useEffect` checks referential equality on
  // `game.player_ids`, the players are fetched again even if the array elements
  // don't change.
  useEffect(refreshPlayers, [
    JSON.stringify(game.player_ids),
    game.current_player_id,
  ]);

  useEffect(() => {
    fetch(`http://localhost:5000/api/players/${playerID}`)
      .then(handleBadRequest)
      .then((data) => setYouPlayer(data))
      .catch((response) => console.log(response));
  }, [playerID, game.current_player_id]);

  function refreshPlayers() {
    const players = game.player_ids.map((id) => {
      return fetch(`http://localhost:5000/api/players/${id}`).then(
        handleBadRequest
      );
    });

    Promise.all(players)
      .then((playersData) => setPlayers(playersData))
      .catch((response) => console.log(response));
  }

  function refreshGame() {
    fetch("http://localhost:5000/api/game")
      .then(handleBadRequest)
      .then((data) => setGame(data))
      .catch((response) => console.log(response));
  }

  function isMyTurn() {
    return game.current_player_id === playerID;
  }

  function canPlay(card) {
    return isMyTurn() && card.playable;
  }

  function playTurn(move, card) {
    if (!canPlay(card)) {
      return;
    }

    fetch("http://localhost:5000/api/game/play", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        move: move,
        card_value: card.value,
        player_id: playerID,
      }),
    })
      .then(handleBadRequest)
      .then((data) => setGame(data.game))
      .catch((response) => console.log(response));
  }

  return (
    <>
      <div className="game">
        <div className="game-state-section">
          <h2>Last Card</h2>
          {game.top_card && (
            <Card
              key={game.top_card.value}
              rank={game.top_card.rank}
              suit={game.top_card.suit}
              displayType={"top-card"}
            />
          )}
        </div>
        <div className="players-section">
          <h2>Players</h2>
          <div>
            {players.map((player) => (
              <div key={player.id}>
                <div
                  className={`player-details ${
                    player.id === game.current_player_id
                      ? "player-details-current"
                      : ""
                  }`}
                >
                  <div
                    className="player-details-id"
                    onClick={() => setPlayerID(player.id)}
                  >{`${player.id} ${
                    player.id === game.current_player_id ? "(to play)" : ""
                  }`}</div>
                  <div>{player.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="you-section">
          <h2>You</h2>
          <div>Player ID: {playerID}</div>
          <div>
            <button
              disabled={!isMyTurn()}
              onClick={() => {
                playTurn("PASS", { value: 0, playable: true });
              }}
            >
              PASS
            </button>
          </div>
          <h3>Cards</h3>
          <div className="card-list">
            {youPlayer.hand.map((card) => (
              <div
                key={card.value}
                onClick={() => {
                  playTurn("PLAY", card);
                }}
              >
                <Card
                  rank={card.rank}
                  suit={card.suit}
                  displayType={
                    canPlay(card) ? "player-card-playable" : "player-card"
                  }
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function handleBadRequest(response) {
  if (response.ok) {
    return response.json();
  } else {
    return Promise.reject(response);
  }
}

export default App;
