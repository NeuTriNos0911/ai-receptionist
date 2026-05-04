import { useState, useCallback } from "react";
import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";
import SimpleVoiceAssistant from "./SimpleVoiceAssistant";

const LiveKitModal = ({ setShowSupport }) => {
  const [isSubmittingName, setIsSubmittingName] = useState(true);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState("");
  const [name, setName] = useState("");
  const [token, setToken] = useState(null);
  const [room, setRoom] = useState(null);
  const liveKitUrl = import.meta.env.VITE_LIVEKIT_URL;

  const checkMicrophonePermission = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("This browser does not support microphone access.");
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      stream.getTracks().forEach((track) => track.stop());
    } catch (error) {
      const permissionError = error?.name === "NotAllowedError" || error?.name === "SecurityError";
      throw new Error(
        permissionError
          ? "Microphone permission is blocked. Allow microphone access for this site, then try again."
          : "Could not access your microphone. Check that a microphone is connected and not used by another app."
      );
    }
  };

  const getToken = useCallback(async (userName) => {
    try {
      setError("");
      setIsConnecting(true);
      await checkMicrophonePermission();
      const response = await fetch(
        `/api/getToken?name=${encodeURIComponent(userName)}`
      );
      const responseText = await response.text();
      const data = responseText ? JSON.parse(responseText) : {};

      if (!response.ok) {
        const missing = data.missing?.length ? ` Missing: ${data.missing.join(", ")}.` : "";
        throw new Error(`${data.error || "Unable to create a support room."}${missing}`);
      }

      if (!data.token) {
        throw new Error("Backend did not return a LiveKit token. Check that the Flask server is running on port 5001.");
      }

      setToken(data.token);
      setRoom(data.room);
      setIsSubmittingName(false);
    } catch (error) {
      console.error(error);
      const isJsonParseError = error instanceof SyntaxError;
      setError(
        isJsonParseError
          ? "Backend returned an invalid response. Make sure the Flask server is running on port 5001."
          : error.message || "Unable to connect. Please try again."
      );
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const handleNameSubmit = (e) => {
    e.preventDefault();
    const trimmedName = name.trim();
    if (!liveKitUrl) {
      setError("Missing VITE_LIVEKIT_URL in frontend/.env.");
      return;
    }

    if (trimmedName) {
      getToken(trimmedName);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="support-room">
          {isSubmittingName ? (
            <form onSubmit={handleNameSubmit} className="name-form">
              <h2>Enter your name to connect with support</h2>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
              />
              {error && <p className="form-error">{error}</p>}
              <button type="submit" disabled={isConnecting}>
                {isConnecting ? "Connecting..." : "Connect"}
              </button>
              <button
                type="button"
                className="cancel-button"
                onClick={() => setShowSupport(false)}
              >
                Cancel
              </button>
            </form>
          ) : token ? (
            <LiveKitRoom
              serverUrl={liveKitUrl}
              token={token}
              connect={true}
              video={false}
              audio={{
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
              }}
              onMediaDeviceFailure={() => {
                setError("Microphone could not be started. Allow mic permission and reconnect.");
                setIsSubmittingName(true);
              }}
              onError={(error) => {
                setError(error.message || "LiveKit connection failed.");
                setIsSubmittingName(true);
              }}
              onDisconnected={() => {
                setShowSupport(false);
                setIsSubmittingName(true);
              }}
            >
              {room && <div className="room-label">Room: {room}</div>}
              <RoomAudioRenderer />
              <SimpleVoiceAssistant />
            </LiveKitRoom>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default LiveKitModal;
