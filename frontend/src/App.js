import React, { useState, useEffect } from "react";
import "./App.css";

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

  function playTurn(move, cardValue) {
    fetch("http://localhost:5000/api/game/play", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        move: move,
        card_value: cardValue,
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
      <p>Last card: {game.top_card && game.top_card.description}</p>
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
            playTurn("PASS", 0);
          }}
        >
          PASS
        </button>
      </div>
      <h3>Cards</h3>
      <div className="card-list">
        {player.hand.map((card) => (
          <div
            key={card.value}
            className={"card " + colorClass(card)}
            disabled={!isMyTurn() || !card.playable}
            onClick={() => {
              playTurn("PLAY", card.value);
            }}
          >
            {String.fromCodePoint(cardAsCodePoint(card))}
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

const codePointSuits = [
  0x1f0c1, // Ace of Diamonds
  0x1f0d1, // Ace of Clubs
  0x1f0b1, // Ace of Hearts
  0x1f0a1, // Ace of Spades
];

function cardAsCodePoint(card) {
  const suitOffset = codePointSuits[card.suit];
  // In President "3" is the lowest, so it has rank 0,
  // so add 2 to get it's rank in normal playing cards.
  var rankOffset = (card.rank + 2) % 13;
  if (rankOffset > 10) {
    // There's a weird "knight" card between Jack and Queen in the Unicode charset
    rankOffset++;
  }
  return suitOffset + rankOffset;
}

function colorClass(card) {
  return card.suit === 0 || card.suit === 2 ? "card-red" : "card-black";
}

export default App;
