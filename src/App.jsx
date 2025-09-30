import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Processing from "./pages/Processing.jsx";
import Outputs from "./pages/Outputs.jsx";
import Results from "./pages/Results.jsx";
import { MeetingProvider } from "./context/MeetingContext.jsx";

function App() {
  return (
    <MeetingProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/processing/:type" element={<Processing />} />
          <Route path="/outputs" element={<Outputs />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </Router>
    </MeetingProvider>
  );
}

export default App;

