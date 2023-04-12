import React, { useState, useEffect } from "react";
import { useMatch } from "react-router-dom";

const RoomPage = () => {
  const [canPause, setCanPause] = useState(false);
  const [votes, setVotes] = useState(2);
  const [isHost, setIsHost] = useState(false);

  const match = useMatch("/room/:roomCode");
  const roomCode = match.params.roomCode;

  useEffect(() => {
    fetch(`/api/v1/get-room/${roomCode}`)
      .then((resp) => resp.json())
      .then((data) => {
        setCanPause(data.guest_can_pause);
        setVotes(data.votes_to_skip);
        setIsHost(data.is_host);
      });
  }, []);

  return (
    <div>
      <h3>ROOM - {roomCode}</h3>
      <p>Votes: {votes}</p>
      <p>Guest Can Pause: {canPause.toString()}</p>
      <p>Host: {isHost.toString()}</p>
    </div>
  );
};

export default RoomPage;
