import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [game, setGame] = useState({player_ids: []});
  const [playerID, setPlayerID] = useState("");

  useEffect(() => {
    fetch('http://localhost:5000/api/game')
      .then(response => response.json())
      .then(data => setGame(data));
  }, []);

  const handleChange = (e) => { setPlayerID(e.target.value) };

  return (
    <>
      <div>
        Player: <input type="text" onChange={handleChange} />
      </div>
      <p>Your turn: {String(playerID === game.current_player_id)}</p>
      <h2>Players</h2>
      <ul>
        {game.player_ids.map((id) => <li key={id}>{id}</li>)}
      </ul>
    </>
  );
}

export default App;
