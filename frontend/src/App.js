import React, { useState } from "react";
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
        <Route exact path="/" render={() => <JoinGame />} />
        <Route
          exact
          path="/game"
          render={(props) => {
            const defaultPlayerID =
              props.location.state && props.location.state.playerID;
            return <Game defaultPlayerID={defaultPlayerID} />;
          }}
        />
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
      <Redirect to={{ pathname: "/game", state: { playerID: playerID } }} />
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
