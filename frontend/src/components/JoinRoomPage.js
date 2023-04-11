import React, { useState } from "react";
import { TextField, Button, Typography, Grid } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";

const JoinRoomPage = () => {
  const [roomCode, setRoomCode] = useState("");
  const [error, setError] = useState("");
  const [isError, setIsError] = useState(false);

  const navigate = useNavigate();

  const handleJoinRoomSubmit = (event) => {
    event.preventDefault();

    const reqOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: roomCode,
      }),
    };

    fetch("/api/v1/join-room", reqOptions)
      .then((resp) => {
        if (resp.ok) {
          navigate(`/room/${roomCode}`);
        } else {
          setIsError(true);
          setError("Room Not Found");
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <Grid container spacing={1}>
      <Grid item xs={12} align="center">
        <Typography variant="h4" component="h4">
          Join A Room
        </Typography>
      </Grid>

      <Grid item xs={12} align="center">
        <TextField
          error={isError}
          label="Code"
          placeholder="Enter a Room Code"
          value={roomCode}
          helperText={error}
          variant="outlined"
          onChange={(e) => setRoomCode(e.target.value)}
        />
      </Grid>

      <Grid item xs={12} align="center">
        <Button
          type="submit"
          variant="contained"
          color="primary"
          onClick={handleJoinRoomSubmit}
        >
          Enter Room
        </Button>
      </Grid>

      <Grid item xs={12} align="center">
        <Button
          type="button"
          variant="contained"
          color="secondary"
          to="/"
          component={Link}
        >
          Back
        </Button>
      </Grid>
    </Grid>
  );
};

export default JoinRoomPage;
