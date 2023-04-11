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

const CreateRoomPage = () => {
  const [canPause, setCanPause] = useState(true);
  const [votes, setVotes] = useState(2);

  const navigate = useNavigate();

  const handleCreateRoomSubmit = (event) => {
    event.preventDefault();

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
    <Grid container spacing={1}>
      <Grid item xs={12} align="center">
        <Typography component="h4" variant="h4">
          Create A Room
        </Typography>
      </Grid>

      <Grid item xs={12} align="center">
        <FormControl component="fieldset">
          <FormHelperText>
            <div align="center">Guest Control of Playback State</div>
          </FormHelperText>

          <RadioGroup
            row
            defaultValue={canPause}
            onChange={(e) => setCanPause(e.target.value)}
          >
            <FormControlLabel
              value="true"
              control={<Radio color="primary" />}
              label="Play/Pause"
              labelPlacement="bottom"
            />
            <FormControlLabel
              value="false"
              control={<Radio color="secondary" />}
              label="No Control"
              labelPlacement="bottom"
            />
          </RadioGroup>
        </FormControl>
      </Grid>

      <Grid item xs={12} align="center">
        <FormControl>
          <TextField
            required={true}
            type="number"
            inputProps={{
              min: 1,
              style: { textAlign: "center" },
            }}
            onChange={(e) => setVotes(e.target.value)}
            defaultValue={votes}
          />
          <FormHelperText>
            <div align="center">Votes Required To Skip Song</div>
          </FormHelperText>
        </FormControl>
      </Grid>

      <Grid item xs={12} align="center">
        <Button
          color="primary"
          variant="contained"
          onClick={handleCreateRoomSubmit}
        >
          Create A Room
        </Button>
      </Grid>

      <Grid item xs={12} align="center">
        <Button color="secondary" variant="contained" to="/" component={Link}>
          Back
        </Button>
      </Grid>
    </Grid>
  );
};

export default CreateRoomPage;
