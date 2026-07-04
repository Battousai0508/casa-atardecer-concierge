# ruff: noqa
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

from typing import Literal, Any

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.workflow import Workflow, node, Edge
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.agents.context import Context
from google.genai import types
from pydantic import BaseModel, Field

from .tools import calendar_mcp


class Classification(BaseModel):
    category: Literal["faq", "calendar", "unrelated"] = Field(
        description="The classified category of the user query."
    )


@node
def preprocess_input(ctx: Context, node_input: Any) -> str:
    """Extracts the text of the user message and saves it to state."""
    text = ""
    if isinstance(node_input, str):
        text = node_input
    elif hasattr(node_input, "parts"):
        text = "".join(part.text for part in node_input.parts if part.text)
    elif isinstance(node_input, dict) and "parts" in node_input:
        parts = node_input["parts"]
        text = "".join(
            p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p
        )
    else:
        text = str(node_input)
    ctx.state["query"] = text
    return text


classifier_agent = LlmAgent(
    name="classifier_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a routing classifier. Analyze the user's message and determine the category:\n"
        "1. 'faq': If the message is related to general stay information, such as check-in/check-out rules, "
        "address, directions, keys, house rules, general questions about the property, or general questions about booking.\n"
        "2. 'calendar': If the message asks about reservations, booking dates availability, booking requests, or calendar scheduling.\n"
        "3. 'unrelated': If the message is unrelated to the vacation rental, Spain, or the guest's stay (e.g. general knowledge, unrelated chatting, etc.).\n"
        "Output ONLY the category inside the schema."
    ),
    output_schema=Classification,
    output_key="classification",
)


@node
def router_node(ctx: Context, node_input: dict) -> Event:
    """Routes the workflow based on the classification and forwards the query."""
    category = node_input.get("category", "unrelated")
    query = ctx.state.get("query", "")
    return Event(output=query, actions=EventActions(route=category))


concierge_faq_agent = LlmAgent(
    name="concierge_faq_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Concierge FAQ Agent for 'Casa Atardecer', a beautiful rural vacation rental in Spain.\n"
        "Answer guest questions about the property, booking process, check-in/out procedures, address, directions, "
        "keys, and house rules. Keep your tone polite, warm, and helpful. Answer in the same language as the guest's query (Spanish or English preferred)."
    ),
)


calendar_agent = LlmAgent(
    name="calendar_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Calendar Agent for 'Casa Atardecer'. You manage reservations and check dates availability.\n"
        "You have access to the owner's Google Calendar via the Google Calendar MCP server tools.\n"
        "\n"
        "CRITICAL RULES FOR BOOKINGS & AVAILABILITY:\n"
        "1. ALWAYS CHECK AVAILABILITY FIRST: Before confirming any booking, scheduling, or calling the `create-event` tool, "
        "you MUST call `list-events` to inspect the calendar for the requested start and end dates.\n"
        "2. DETECT OVERLAPS: If `list-events` returns ANY event that overlaps with the guest's requested stay "
        "(from check-in date to check-out date), you MUST reject the request. Inform the guest politely that those dates "
        "are already booked or unavailable, and suggest they choose alternative dates. NEVER create overlapping events.\n"
        "3. TREATING SLOTS AS BUSY: Any event found in the calendar (specifically events with titles like 'reservado', 'Reservado', 'Reserva', 'Ocupado', 'Mantenimiento', or personal events) "
        "means the slot is busy and is NOT available for booking on that day. Do not make assumptions that a slot is free if there is an event present.\n"
        "4. RESPOND IN THE GUEST'S LANGUAGE: Keep your tone polite, warm, and professional. Use Spanish or English as appropriate."
    ),
    tools=[calendar_mcp],
)


@node
def decline_node(ctx: Context, node_input: str) -> Event:
    """Politely declines to answer unrelated queries and redirects to stay topics."""
    msg = (
        "Lo siento, solo puedo responder preguntas relacionadas con su estancia en Casa Atardecer "
        "(como indicaciones para llegar, llaves, normas de la casa, disponibilidad o reservas). "
        "¿En qué puedo ayudarle respecto a su estancia?\n\n"
        "Sorry, I can only answer questions related to your stay at Casa Atardecer "
        "(such as directions, keys, house rules, availability, or reservations). "
        "How can I help you regarding your stay?"
    )
    return Event(
        output=msg,
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=msg)],
        ),
    )


root_agent = Workflow(
    name="casa_atardecer_workflow",
    edges=[
        ("START", preprocess_input),
        (preprocess_input, classifier_agent),
        (classifier_agent, router_node),
        Edge(from_node=router_node, to_node=concierge_faq_agent, route="faq"),
        Edge(from_node=router_node, to_node=calendar_agent, route="calendar"),
        Edge(from_node=router_node, to_node=decline_node, route="unrelated"),
    ],
)


app = App(
    root_agent=root_agent,
    name="app",
)
