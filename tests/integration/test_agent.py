# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from typing import Any

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


def _run_agent(user_query: str) -> tuple[InMemorySessionService, Any]:
    # Sleep to avoid hitting Gemini free tier rate limits (5 requests per minute)
    time.sleep(15)

    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="app")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="app")

    message = types.Content(role="user", parts=[types.Part.from_text(text=user_query)])

    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    updated_session = session_service.get_session_sync(
        app_name="app", user_id="test_user", session_id=session.id
    )
    return updated_session, events


def test_faq_route() -> None:
    """Verifies that an FAQ query is correctly classified and answered by the FAQ agent."""
    session, events = _run_agent("Where is Casa Atardecer located?")

    # Check classification state
    classification = session.state.get("classification")
    assert classification is not None
    assert classification.get("category") == "faq"

    # Check that we got a textual response containing stay details
    response_text = ""
    for event in events:
        if event.content and event.content.parts:
            response_text += "".join(p.text for p in event.content.parts if p.text)

    assert len(response_text) > 0
    assert (
        "Casa Atardecer" in response_text
        or "ubicada" in response_text
        or "located" in response_text
    )


def test_calendar_route() -> None:
    """Verifies that calendar/reservation queries route to the calendar agent."""
    session, _ = _run_agent("Is the house available next weekend?")

    classification = session.state.get("classification")
    assert classification is not None
    assert classification.get("category") == "calendar"


def test_unrelated_route() -> None:
    """Verifies that unrelated queries are classified as unrelated and politely declined."""
    session, events = _run_agent("What is the capital of France?")

    classification = session.state.get("classification")
    assert classification is not None
    assert classification.get("category") == "unrelated"

    response_text = ""
    for event in events:
        if event.content and event.content.parts:
            response_text += "".join(p.text for p in event.content.parts if p.text)

    assert "Sorry" in response_text or "Lo siento" in response_text
