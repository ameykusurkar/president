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
        <Route exact path="/" component={JoinGame} />
        <Route exact path="/waiting" component={Waiting} />
        <Route exact path="/game" component={Game} />
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
    return (
      <Redirect to={{ pathname: "/waiting", state: { playerID: playerID } }} />
    );
  } else {
    return (
      <div id="join-screen" className="centered-screen-box-outer">
        <div className="centered-screen-box">
          <div id="join-game-player-id">
            <div>Player ID</div>
            <input
              id="join-game-input"
              type="text"
              onChange={(e) => setPlayerID(e.target.value)}
            />
          </div>
          <div id="join-game-box-button-outer">
            <button onClick={joinGame}>Join Game</button>
          </div>
        </div>
      </div>
    );
  }
}

function Waiting(props) {
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
      <div id="waiting-screen" className="centered-screen-box-outer">
        <div className="centered-screen-box">
          <h2>Waiting...</h2>
          <div>
            <button onClick={startGame}>Start Game</button>
          </div>
          <h3>Joined So Far</h3>
          {game.waiting_player_ids &&
            game.waiting_player_ids.map((id) => (
              <div
                key={id}
                style={{
                  fontWeight:
                    id === props.location.state.playerID ? "bold" : "normal",
                }}
              >
                {id}
              </div>
            ))}
        </div>
      </div>
    );
  } else {
    return <Redirect to="/game" />;
  }
}
