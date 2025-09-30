import { createContext, useState, useEffect } from "react";
import axios from "axios";

export const MeetingContext = createContext();

export const MeetingProvider = ({ children }) => {
  const [meetingId, setMeetingId] = useState(null);
  const [loading, setLoading] = useState(true);  // Fixed to true initially

  useEffect(() => {
    const initializeMeeting = async () => {
      const storedId = localStorage.getItem("meetingId");

      if (storedId) {
        try {
          await axios.get(`http://localhost:8000/meetings/${storedId}`);
          setMeetingId(storedId);
          setLoading(false);
          return;
        } catch {
          localStorage.removeItem("meetingId");
        }
      }

      try {
        const res = await axios.post("http://localhost:8000/meetings", {
          title: `Meeting_${new Date().toISOString().split("T")[0]}`,
          date: new Date().toISOString().split("T")[0],
          created_by: "User",
        });
        setMeetingId(res.data.id);
        localStorage.setItem("meetingId", res.data.id);
      } catch (error) {
        console.error("Error creating meeting:", error);
      } finally {
        setLoading(false);
      }
    };

    initializeMeeting();
  }, []);

  const createNewMeeting = async (title, date, createdBy) => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/meetings", {
        title: title || `Meeting_${new Date().toISOString().split("T")[0]}`,
        date: date || new Date().toISOString().split("T")[0],
        created_by: createdBy || "User",
      });
      setMeetingId(res.data.id);
      localStorage.setItem("meetingId", res.data.id);
      return res.data.id;
    } catch (error) {
      console.error("Error creating meeting:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const clearMeeting = () => {
    setMeetingId(null);
    localStorage.removeItem("meetingId");
  };

  return (
    <MeetingContext.Provider 
      value={{ meetingId, setMeetingId, loading, setLoading, createNewMeeting, clearMeeting }}
    >
      {children}
    </MeetingContext.Provider>
  );
};
