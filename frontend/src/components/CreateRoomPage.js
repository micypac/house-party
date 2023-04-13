import React, { useState } from "react";
import {
  Button,
  Grid,
  Typography,
  TextField,
  FormHelperText,
  FormControl,
  FormControlLabel,
  RadioGroup,
  Radio,
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import RoomFormPage from "./RoomFormPage";

const CreateRoomPage = () => {
  const [canPause, setCanPause] = useState(true);
  const [votes, setVotes] = useState(2);

  const navigate = useNavigate();

  const handleCreateRoomSubmit = () => {
    // event.preventDefault();

    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        votes_to_skip: votes,
        guest_can_pause: canPause,
      }),
    };

    fetch("/api/v1/create-room", requestOptions)
      .then((resp) => resp.json())
      // .then((data) => console.log(data));
      .then((data) => navigate(`/room/${data.code}`));
  };

  return (
    <>
      <RoomFormPage
        mode="create"
        canPause={canPause}
        setCanPause={setCanPause}
        votes={votes}
        setVotes={setVotes}
        handleSubmit={() => handleCreateRoomSubmit()}
      />
      <Grid item xs={12} align="center">
        <Button
          type="button"
          color="secondary"
          variant="contained"
          to="/"
          component={Link}
        >
          Back
        </Button>
      </Grid>
    </>
  );
};

export default CreateRoomPage;
