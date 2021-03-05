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
          path="/games/:id"
          render={(props) => {
            const defaultPlayerID =
              props.location.state && props.location.state.playerID;
            return (
              <Game
                defaultPlayerID={defaultPlayerID}
                gameID={props.match.params.id}
              />
            );
          }}
        />
      </Switch>
    </Router>
  );
}

function JoinGame() {
  const [joined, setJoined] = useState(false);
  const [playerID, setPlayerID] = useState("");
  const [gameID, setGameID] = useState("");

  function joinGame() {
    fetch(`${BASE_URL}/games/${gameID}/join`, {
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
      <Redirect
        to={{
          pathname: `/games/${gameID}`,
          state: { playerID: playerID },
        }}
      />
    );
  } else {
    return (
      <div id="join-screen" className="centered-screen-box-outer">
        <div className="centered-screen-box">
          <div className="join-game-form-box">
            <div className="join-game-label">Game ID</div>
            <input
              className="join-game-input"
              type="text"
              onChange={(e) => setGameID(e.target.value)}
            />
          </div>
          <div className="join-game-form-box">
            <div className="join-game-label">Player ID</div>
            <input
              className="join-game-input"
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
