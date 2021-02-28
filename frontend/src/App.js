import React from "react";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import "./App.css";
import Game from "./Game";

export default function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/">
          <h2>Hello, World!</h2>
          <Link to="/game">Game</Link>
        </Route>
        <Route path="/game">
          <Game />
        </Route>
      </Switch>
    </Router>
  );
}
