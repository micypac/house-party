import React from "react";
import { Routes, Route } from "react-router-dom";

import CreateRoomPage from "./CreateRoomPage";
import JoinRoomPage from "./JoinRoomPage";
import RoomPage from "./RoomPage";

const HomePage = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<p>This is the home page</p>} />
        <Route path="/create" element={<CreateRoomPage />} />
        <Route path="/join" element={<JoinRoomPage />} />
        <Route path="/room/:roomCode" element={<RoomPage />} />
      </Routes>
    </div>
  );
};

export default HomePage;
