import React, { useState, useEffect } from "react";
import { Routes, Route, Link, Navigate } from "react-router-dom";

import CreateRoomPage from "./CreateRoomPage";
import JoinRoomPage from "./JoinRoomPage";
import RoomPage from "./RoomPage";

import { Grid, Button, ButtonGroup, Typography } from "@mui/material";

const HomePage = () => {
  const [roomCode, setRoomCode] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const resp = await fetch("/api/v1/user-in-room");
      const data = await resp.json();

      setRoomCode(data.code);
    };

    fetchData().catch(console.error);

    // fetch("/api/v1/user-in-room")
    //   .then((resp) => resp.json())
    //   .then((data) => {
    //     setRoomCode(data.code);
    //   });
  }, []);

  const content = (
    <Grid container spacing={3}>
      <Grid item xs={12} align="center">
        <Typography variant="h3" component="h3">
          House Party
        </Typography>
      </Grid>

      <Grid item xs={12} align="center">
        <ButtonGroup disableElevation variant="contained" color="primary">
          <Button color="primary" to="/join" component={Link}>
            Join A Room
          </Button>
          <Button color="secondary" to="/create" component={Link}>
            Create A Room
          </Button>
        </ButtonGroup>
      </Grid>
    </Grid>
  );

  return (
    <div>
      <Routes>
        <Route
          path="/"
          element={roomCode ? <Navigate to={`/room/${roomCode}`} /> : content}
        />
        <Route path="/create" element={<CreateRoomPage />} />
        <Route path="/join" element={<JoinRoomPage />} />
        <Route path="/room/:roomCode" element={<RoomPage />} />
      </Routes>
    </div>
  );
};

export default HomePage;
