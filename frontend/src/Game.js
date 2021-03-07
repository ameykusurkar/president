import React, { useState, useEffect } from "react";
import Card from "./Card";

const BASE_URL = `${process.env.REACT_APP_SERVER_URL}/api`;

function Game({ defaultPlayerID, gameID }) {
  const [game, setGame] = useState({ status: "loading" });
  const [playerID, setPlayerID] = useState(defaultPlayerID);
  const [youPlayer, setYouPlayer] = useState({ hand: [] });

  useEffect(() => {
    document.title = "President!";
    const interval = setInterval(refreshGame, 2000);
    return () => {
      clearInterval(interval);
    };
  // eslint-disable-next-line
  }, []);

  useEffect(() => {
    fetch(`${BASE_URL}/games/${gameID}/players/${playerID}`)
      .then(handleBadRequest)
      .then((data) => setYouPlayer(data))
      .catch((response) => console.log(response));
  }, [gameID, playerID, game.turn_number]);

  function refreshGame() {
    fetch(`${BASE_URL}/games/${gameID}`)
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

    fetch(`${BASE_URL}/games/${gameID}/play`, {
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

  if (game.status === "loading") {
    return "Loading...";
  }

  if (game.status === "waiting") {
    return (
      <Waiting
        gameID={gameID}
        playerIds={game.player_ids}
        playerID={playerID}
      />
    );
  }

  return (
    <>
      <div id="game">
        <div id="game-state-section">
          <h3>Turn {game.turn_number}</h3>
          <h2>Last Card</h2>
          {game.last_card ? (
            <Card
              rank={game.last_card.rank}
              suit={game.last_card.suit}
              displayType={"top-card"}
            />
          ) : (
            <Card rank={-1} displayType={"top-card"} />
          )}
        </div>
        <div id="players-section">
          <h2>Players</h2>
          <Players
            gameID={gameID}
            playerIds={game.player_ids}
            turnNo={game.turn_number}
            currentPlayerId={game.current_player_id}
            setPlayerID={setPlayerID}
          />
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
              {youPlayer.hand
                .sort((a, b) => a.rank - b.rank)
                .map((card) => (
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

function Waiting({ gameID, playerIds, playerID }) {
  function startGame() {
    fetch(`${BASE_URL}/games/${gameID}/start`, { method: "POST" })
      .then(handleBadRequest)
      .then((data) => console.log("started game"))
      .catch((response) => console.log(response));
  }

  return (
    <div id="waiting-screen" className="centered-screen-box-outer">
      <div className="centered-screen-box">
        <h2>Waiting...</h2>
        {playerIds.length >= 2 && (
          <div>
            <button onClick={startGame}>Start Game</button>
          </div>
        )}
        <h3>Joined So Far</h3>
        {playerIds &&
          playerIds.map((id) => (
            <div
              key={id}
              style={{
                fontWeight: id === playerID ? "bold" : "normal",
              }}
            >
              {id}
            </div>
          ))}
      </div>
    </div>
  );
}

function Players({ gameID, playerIds, turnNo, currentPlayerId, setPlayerID }) {
  const [players, setPlayers] = useState([]);

  // TODO: Find a good fix for this. Because `useEffect` checks referential equality on
  // `game.player_ids`, the players are fetched again even if the array elements
  // don't change.
  // eslint-disable-next-line
  useEffect(refreshPlayers, [JSON.stringify(playerIds), turnNo]);

  function refreshPlayers() {
    const players = playerIds.map((id) => {
      return fetch(`${BASE_URL}/games/${gameID}/players/${id}`).then(
        handleBadRequest
      );
    });

    Promise.all(players)
      .then((playersData) => setPlayers(playersData))
      .catch((response) => console.log(response));
  }

  function playerStatus(player) {
    if (player.user_id === currentPlayerId) {
      return "TO PLAY";
    }

    return player.status !== "ACTIVE" ? player.status : "";
  }

  return (
    <div id="players-list">
      {players
        .sort((a, b) => a.game_player_index - b.game_player_index)
        .map((player) => (
          <div key={player.id}>
            <div
              onClick={() => setPlayerID(player.user_id)}
              className={`player-details ${
                player.user_id === currentPlayerId
                  ? "player-details-current"
                  : ""
              }`}
            >
              <div className="player-details-id">{player.user_id}</div>
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
  );
}

function handleBadRequest(response) {
  if (response.ok) {
    return response.json();
  } else {
    return Promise.reject(response);
  }
}

export { Game, BASE_URL, handleBadRequest };
