import { useNavigate } from "react-router-dom";
import OptionCard from "../components/OptionCard";
import "./Home.css";

function Home() {
  const navigate = useNavigate();

  const options = [
    {
      title: "Text Transcript",
      desc: "Paste your meeting notes or transcript",
      icon: "📄",
      type: "text",
      color: "blue",
    },
    {
      title: "Whiteboard Photo",
      desc: "Upload photos of whiteboards or notes",
      icon: "📷",
      type: "photo",
      color: "pink",
    },
    {
      title: "Audio Recording",
      desc: "Upload meeting audio or voice memos",
      icon: "🎤",
      type: "audio",
      color: "purple",
    },
  ];

  const handleSelect = (type) => {
    navigate(`/processing/${type}`);
  };

  return (
    <div className="home">
      <div className="header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <div className="title-block">
          <h1 className="title">
            Choose Your Meeting Input <span>📝</span>
          </h1>
          <p className="subtitle">
            How would you like to share your meeting content?
          </p>
        </div>
      </div>

      <div className="options-grid">
        {options.map((opt) => (
          <OptionCard
            key={opt.type}
            {...opt}
            onSelect={() => handleSelect(opt.type)}
          />
        ))}
      </div>
    </div>
  );
}

export default Home;
