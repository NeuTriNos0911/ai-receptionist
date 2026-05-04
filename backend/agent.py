from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli
)
from livekit.plugins import openai
from openai.types import realtime
from dotenv import load_dotenv
import os

load_dotenv()

from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
    model = openai.realtime.RealtimeModel(
        model=os.getenv("OPENAI_REALTIME_MODEL", "gpt-realtime"),
        voice=os.getenv("ASSISTANT_VOICE", "marin"),
        input_audio_transcription=realtime.AudioTranscription(
            model=os.getenv("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-transcribe")
        ),
        modalities=["audio", "text"]
    )

    assistant = AssistantFnc(instructions=INSTRUCTIONS)
    session = AgentSession(llm=model)
    await session.start(agent=assistant, room=ctx.room)
    session.generate_reply(instructions=WELCOME_MESSAGE)
    
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
