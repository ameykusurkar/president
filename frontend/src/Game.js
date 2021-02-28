import React, { useState, useEffect } from "react";
import Card from "./Card";

const BASE_URL = "http://localhost:5000/api";

export default function Game() {
  const [game, setGame] = useState({ player_ids: [] });
  const [players, setPlayers] = useState([]);
  const [playerID, setPlayerID] = useState("");
  const [youPlayer, setYouPlayer] = useState({ hand: [] });

  useEffect(() => {
    document.title = "President!";
    const interval = setInterval(refreshGame, 2000);
    return () => {
      clearInterval(interval);
    };
  }, []);

  // TODO: Find a good fix for this. Because `useEffect` checks referential equality on
  // `game.player_ids`, the players are fetched again even if the array elements
  // don't change.
  useEffect(refreshPlayers, [JSON.stringify(game.player_ids), game.turn_no]);

  useEffect(() => {
    fetch(`${BASE_URL}/players/${playerID}`)
      .then(handleBadRequest)
      .then((data) => setYouPlayer(data))
      .catch((response) => console.log(response));
  }, [playerID, game.turn_no]);

  function refreshPlayers() {
    const players = game.player_ids.map((id) => {
      return fetch(`${BASE_URL}/players/${id}`).then(handleBadRequest);
    });

    Promise.all(players)
      .then((playersData) => setPlayers(playersData))
      .catch((response) => console.log(response));
  }

  function refreshGame() {
    fetch(`${BASE_URL}/game`)
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

  function playerStatus(player) {
    if (player.id === game.current_player_id) {
      return "TO PLAY";
    }

    return player.status !== "ACTIVE" ? player.status : "";
  }

  function playTurn(move, card) {
    if (!canPlay(card)) {
      return;
    }

    fetch(`${BASE_URL}/game/play`, {
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
      <div id="game">
        <div id="game-state-section">
          <h3>Turn {game.turn_no}</h3>
          <h2>Last Card</h2>
          {game.top_card ? (
            <Card
              rank={game.top_card.rank}
              suit={game.top_card.suit}
              displayType={"top-card"}
            />
          ) : (
            <Card rank={-1} displayType={"top-card"} />
          )}
        </div>
        <div id="players-section">
          <h2>Players</h2>
          <div id="players-list">
            {players.map((player) => (
              <div key={player.id}>
                <div
                  onClick={() => setPlayerID(player.id)}
                  className={`player-details ${
                    player.id === game.current_player_id
                      ? "player-details-current"
                      : ""
                  }`}
                >
                  <div className="player-details-id">{player.id}</div>
                  <div className="player-details-num-cards">
                    {`${String.fromCodePoint(0x1f0a0)} ${player.hand.length}`}
                  </div>
                  <div className="player-details-status">
                    {playerStatus(player)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div id="you-section">
          <h2>{playerID}</h2>
          <div id="you-section-pass">
            <button
              disabled={!isMyTurn()}
              onClick={() => {
                playTurn("PASS", { value: 0, playable: true });
              }}
            >
              PASS
            </button>
          </div>
          <div id="card-list-box">
            <div id="card-list">
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
