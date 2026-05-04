import os
from livekit import api
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from livekit.api import LiveKitAPI, ListRoomsRequest
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

REQUIRED_ENV = ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")

def missing_env():
    return [key for key in REQUIRED_ENV if not os.getenv(key)]

async def generate_room_name():
    name = "room-" + str(uuid.uuid4())[:8]
    rooms = await get_rooms()
    while name in rooms:
        name = "room-" + str(uuid.uuid4())[:8]
    return name

async def get_rooms():
    api = LiveKitAPI()
    rooms = await api.room.list_rooms(ListRoomsRequest())
    await api.aclose()
    return [room.name for room in rooms.rooms]

@app.route("/health")
def health():
    missing = missing_env()
    return jsonify({
        "ok": not missing,
        "missing": missing
    }), 200 if not missing else 503

@app.route("/getToken")
async def get_token():
    missing = missing_env()
    if missing:
        return jsonify({
            "error": "Missing required backend environment variables.",
            "missing": missing
        }), 500

    name = request.args.get("name", "my name")
    room = request.args.get("room", None)
    
    if not room:
        room = await generate_room_name()
        
    token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")) \
        .with_identity(name)\
        .with_name(name)\
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room
        ))
    
    return jsonify({
        "token": token.to_jwt(),
        "room": room
    })

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5001, debug=debug, use_reloader=debug)
