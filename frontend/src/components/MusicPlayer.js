import React from "react";
import {
  Grid,
  Typography,
  Card,
  IconButton,
  LinearProgress,
} from "@mui/material";
import PauseIcon from "@mui/icons-material/Pause";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import SkipNextIcon from "@mui/icons-material/SkipNext";

const MusicPlayer = ({ song }) => {
  const songProgress = (song.time / song.duration) * 100;

  const handlePlaySubmit = () => {
    const reqOptions = {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
    };

    fetch("/spotify/play", reqOptions);
  };

  const handlePauseSubmit = () => {
    const reqOptions = {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
    };

    fetch("/spotify/pause", reqOptions);
  };

  return (
    <Card>
      <Grid container spacing={1}>
        <Grid item xs={4} align="center">
          <img src={song.img_url} height="100%" width="100%" />
        </Grid>

        <Grid item xs={8} align="center">
          <Typography variant="h5" component="h5">
            {song.title}
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            {song.artist}
          </Typography>
          <div>
            <IconButton
              onClick={() => {
                song.is_playing ? handlePauseSubmit() : handlePlaySubmit();
              }}
            >
              {song.is_playing ? <PauseIcon /> : <PlayArrowIcon />}
            </IconButton>
            <IconButton>
              <SkipNextIcon />
            </IconButton>
          </div>
        </Grid>
      </Grid>

      <LinearProgress variant="determinate" value={songProgress} />
    </Card>
  );
};

export default MusicPlayer;
