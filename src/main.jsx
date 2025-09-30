import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import { MeetingProvider } from "./context/MeetingContext.jsx"; // Update this line
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <MeetingProvider>
      <App />
    </MeetingProvider>
  </React.StrictMode>
);
