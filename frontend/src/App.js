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
        <Route exact path="/" render={() => <CreateGame />} />
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

function CreateGame() {
  const [playerID, setPlayerID] = useState("");
  const [gameID, setGameID] = useState(null);
  const [error, setError] = useState(null);

  function createGame() {
    fetch(`${BASE_URL}/games`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ player_id: playerID }),
    })
      .then(handleBadRequest)
      .then((data) => setGameID(data.id))
      .catch((response) => {
        console.log(response);
        setError(response.errors[0]);
      });
  }

  if (gameID) {
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
            <div className="join-game-label">Player ID</div>
            <input
              className="join-game-input"
              type="text"
              onChange={(e) => setPlayerID(e.target.value)}
            />
            {error && <div className="join-game-error">{error}</div>}
          </div>
          <div id="join-game-box-button-outer">
            <button onClick={createGame}>START NEW GAME</button>
          </div>
        </div>
      </div>
    );
  }
}
