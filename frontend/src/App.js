import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [game, setGame] = useState({ player_ids: [] });
  const [playerID, setPlayerID] = useState("");
  const [player, setPlayer] = useState({ hand: [] });

  useEffect(refreshGame, []);

  useEffect(() => {
    fetch(`http://localhost:5000/api/players/${playerID}`)
      .then(handleBadRequest)
      .then((data) => setPlayer(data))
      .catch((response) => console.log(response));
  }, [playerID]);

  function handleClick(e) {
    setPlayerID(e.target.innerHTML);
  }

  function refreshGame() {
    fetch("http://localhost:5000/api/game")
      .then(handleBadRequest)
      .then((data) => setGame(data))
      .catch((response) => console.log(response));
  }

  return (
    <>
      <p>Whose turn: {game.current_player_id}</p>
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
      <h3>Cards</h3>
      <ul>
        {player.hand.map((card) => (
          <li key={card.value}>
            {card.description + (card.playable ? " (playable)" : "")}
          </li>
        ))}
      </ul>
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
