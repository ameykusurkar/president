import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Switch,
  Route,
} from "react-router-dom";
import "./App.css";
import { Game, handleBadRequest, BASE_URL } from "./Game";

export default function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/">
          <JoinGame />
        </Route>
        <Route exact path="/waiting">
          <Waiting />
        </Route>
        <Route path="/game">
          <Game />
        </Route>
      </Switch>
    </Router>
  );
}

function JoinGame() {
  const [joined, setJoined] = useState(false);
  const [playerID, setPlayerID] = useState("");

  function joinGame() {
    fetch(`${BASE_URL}/game/join`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ player_id: playerID }),
    })
      .then(handleBadRequest)
      .then((data) => setJoined(true))
      .catch((response) => console.log(response));
  }

  if (joined) {
    return <Redirect to="/waiting" />;
  } else {
    return (
      <div id="join-game-box">
        <div>Player ID:</div>
        <div>
          <input type="text" onChange={(e) => setPlayerID(e.target.value)} />
        </div>
        <div>
          <button onClick={joinGame}>Join Game</button>
        </div>
      </div>
    );
  }
}

function Waiting() {
  const [game, setGame] = useState({ game_status: "waiting" });

  useEffect(() => {
    const interval = setInterval(refreshGame, 2000);
    return () => {
      clearInterval(interval);
    };
  }, []);

  function refreshGame() {
    fetch(`${BASE_URL}/game`)
      .then(handleBadRequest)
      .then((data) => setGame(data))
      .catch((response) => console.log(response));
  }

  function startGame() {
    fetch(`${BASE_URL}/game/start`, { method: "POST" })
      .then(handleBadRequest)
      .then((data) => console.log("started game"))
      .catch((response) => console.log(response));
  }

  if (game.game_status === "waiting") {
    return (
      <div>
        <h2>Waiting to start game...</h2>
        <h3>Joined so far</h3>
        {game.waiting_player_ids &&
          game.waiting_player_ids.map((id) => <div key={id}>{id}</div>)}
        <div>
          <button onClick={startGame}>Start Game</button>
        </div>
      </div>
    );
  } else {
    return <Redirect to="/game" />;
  }
}
