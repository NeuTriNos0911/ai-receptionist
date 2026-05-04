import {
  useVoiceAssistant,
  BarVisualizer,
  VoiceAssistantControlBar,
  useTrackTranscription,
  useLocalParticipant,
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { useEffect, useState } from "react";
import "./SimpleVoiceAssistant.css";

const Message = ({ type, text }) => {
  return <div className="message">
    <strong className={`message-${type}`}>
      {type === "agent" ? "Agent: " : "You: "}
    </strong>
    <span className="message-text">{text}</span>
  </div>;
};

const SimpleVoiceAssistant = () => {
  const { agent, state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  const { isMicrophoneEnabled, lastMicrophoneError, localParticipant, microphoneTrack } = useLocalParticipant();
  const localMicrophoneRef = microphoneTrack
    ? {
        participant: localParticipant,
        publication: microphoneTrack,
        source: Track.Source.Microphone,
      }
    : undefined;
  const { segments: userTranscriptions } = useTrackTranscription(localMicrophoneRef);

  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const allMessages = [
      ...(agentTranscriptions?.map((t) => ({ ...t, type: "agent" })) ?? []),
      ...(userTranscriptions?.map((t) => ({ ...t, type: "user" })) ?? []),
    ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
    setMessages(allMessages);
  }, [agentTranscriptions, userTranscriptions]);

  return (
    <div className="voice-assistant-container">
      <div className="visualizer-container">
        <BarVisualizer state={state} barCount={7} trackRef={audioTrack} />
      </div>
      <div className="control-section">
        <div className={`agent-status ${agent ? "agent-ready" : "agent-waiting"}`}>
          {agent
            ? "AI receptionist is connected"
            : "Waiting for AI receptionist worker to join"}
        </div>
        <div className={`mic-status ${isMicrophoneEnabled ? "mic-on" : "mic-off"}`}>
          {isMicrophoneEnabled
            ? "Microphone is on"
            : "Microphone is muted. Click the mic icon to turn it on."}
          {lastMicrophoneError && <span> {lastMicrophoneError.message}</span>}
        </div>
        <VoiceAssistantControlBar />
        <div className="conversation">
          {messages.map((msg, index) => (
            <Message key={msg.id || index} type={msg.type} text={msg.text} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default SimpleVoiceAssistant;
