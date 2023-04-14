import React, { useState, useEffect } from "react";
import { useMatch, useNavigate } from "react-router-dom";
import { Grid, Button, Typography } from "@mui/material";
import RoomFormPage from "./RoomFormPage";

const RoomPage = ({ clearCode }) => {
  const [canPause, setCanPause] = useState(false);
  const [origCanPause, setOrigCanPause] = useState(false);
  const [votes, setVotes] = useState(2);
  const [origVotes, setOrigVotes] = useState(2);
  const [isHost, setIsHost] = useState(false);

  const [showSettings, setShowSettings] = useState(false);
  const [spotifyAuth, setSpotifyAuth] = useState(false);

  const match = useMatch("/room/:roomCode");
  const roomCode = match.params.roomCode;

  const navigate = useNavigate();

  useEffect(() => {
    const fetchRoomData = async () => {
      const resp = await fetch(`/api/v1/get-room/${roomCode}`);
      if (!resp.ok) {
        clearCode();
        navigate("/");
      }

      const data = await resp.json();

      setCanPause(data.guest_can_pause);
      setVotes(data.votes_to_skip);
      setIsHost(data.is_host);
    };

    fetchRoomData().catch(console.error);
  }, []);

  useEffect(() => {
    console.log(`isHost: ${isHost}`);

    if (isHost) {
      authenticateSpotify();
    }
  }, [isHost]);

  const authenticateSpotify = async () => {
    let resp = await fetch("/spotify/is-authenticated");
    let data = await resp.json();

    setSpotifyAuth(data.status);
    console.log(`Spotify Auth: ${spotifyAuth}`);

    if (!data.status) {
      resp = await fetch("/spotify/get-auth-url");
      data = await resp.json();
      window.location.replace(data.url);
    }
  };

  const handleLeaveRoomSubmit = async (event) => {
    event.preventDefault();

    const reqOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const resp = await fetch("/api/v1/leave-room", reqOptions);
    clearCode();
    navigate("/");
  };

  const handleUpdateRoomSubmit = () => {
    const reqOptions = {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code: roomCode,
        guest_can_pause: canPause,
        votes_to_skip: votes,
      }),
    };

    fetch("/api/v1/update-room", reqOptions).then((resp) => {
      if (resp.ok) {
        console.log("Room Update Success");
        setShowSettings(false);
      } else {
        console.log("Room Update Failed");
        setShowSettings(false);
      }
    });
  };

  const handleShowSettingsButton = () => {
    setOrigCanPause(canPause);
    setOrigVotes(votes);
    setShowSettings(!showSettings);
  };

  const detailContent = (
    <Grid container spacing={1}>
      <Grid item xs={12} align="center">
        <Typography variant="h4" component="h4">
          Room Code: {roomCode}
        </Typography>
      </Grid>
      <Grid item xs={12} align="center">
        <Typography variant="h6" component="h6">
          Votes: {votes}
        </Typography>
      </Grid>
      <Grid item xs={12} align="center">
        <Typography variant="h6" component="h6">
          Guest Can Pause: {canPause.toString()}
        </Typography>
      </Grid>
      <Grid item xs={12} align="center">
        <Typography variant="h6" component="h6">
          Host: {isHost.toString()}
        </Typography>
      </Grid>

      {!isHost ? null : (
        <Grid item xs={12} align="center">
          <Button
            type="button"
            variant="contained"
            color="primary"
            onClick={handleShowSettingsButton}
          >
            Show Settings
          </Button>
        </Grid>
      )}

      <Grid item xs={12} align="center">
        <Button
          type="submit"
          variant="contained"
          color="secondary"
          onClick={handleLeaveRoomSubmit}
        >
          Leave Room
        </Button>
      </Grid>
    </Grid>
  );

  if (showSettings) {
    return (
      <>
        <RoomFormPage
          mode="update"
          canPause={canPause}
          setCanPause={setCanPause}
          votes={votes}
          setVotes={setVotes}
          handleSubmit={() => handleUpdateRoomSubmit()}
        />

        <Grid item xs={12} align="center">
          <Button
            type="button"
            color="secondary"
            variant="contained"
            onClick={() => {
              setVotes(origVotes);
              setCanPause(origCanPause);
              setShowSettings(false);
            }}
          >
            Back
          </Button>
        </Grid>
      </>
    );
  } else {
    return detailContent;
  }
};

export default RoomPage;
