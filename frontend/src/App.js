import React, { useState, useEffect } from "react";
import "./App.css";
import Card from "./Card";

function App() {
  const [game, setGame] = useState({ player_ids: [] });
  const [playerID, setPlayerID] = useState("");
  const [player, setPlayer] = useState({ hand: [] });

  useEffect(() => {
    const interval = setInterval(refreshGame, 2000);
    return () => {
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    fetch(`http://localhost:5000/api/players/${playerID}`)
      .then(handleBadRequest)
      .then((data) => setPlayer(data))
      .catch((response) => console.log(response));
  }, [playerID, game.current_player_id]);

  function handleClick(e) {
    setPlayerID(e.target.innerHTML);
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
      <h1>President</h1>
      <p>Whose turn: {game.current_player_id}</p>
      <p>
        Last card:{" "}
        {game.top_card && (
          <Card
            key={game.top_card.value}
            rank={game.top_card.rank}
            suit={game.top_card.suit}
            playable={true} // Not playable, but render in full color
          />
        )}
      </p>
      <h2>Players</h2>
      <div>
        {game.player_ids.map((id) => (
          <div key={id}>
            <button onClick={handleClick}>{id}</button>
          </div>
        ))}
      </div>
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
        {player.hand.map((card) => (
          <div
            onClick={() => {
              playTurn("PLAY", card);
            }}
          >
            <Card
              key={card.value}
              rank={card.rank}
              suit={card.suit}
              playable={canPlay(card)}
            />
          </div>
        ))}
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
