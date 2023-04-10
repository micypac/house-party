import React from "react";
import { Routes, Route } from "react-router-dom";

import CreateRoomPage from "./CreateRoomPage";
import JoinRoomPage from "./JoinRoomPage";

const HomePage = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<p>This is the home page</p>} />
        <Route path="/create" element={<CreateRoomPage />} />
        <Route path="/join" element={<JoinRoomPage />} />
      </Routes>
    </div>
  );
};

export default HomePage;
