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

"""Casa Atardecer Concierge — agent definition.

Design overview
---------------
This module wires a **router-based multi-agent workflow** rather than a single
"do-everything" agent. Each guest message flows through:

    preprocess_input -> classifier_agent -> router_node -> [specialist]

We deliberately split the work into small, single-responsibility agents because:

* **Focused prompts evaluate better.** A narrow instruction (only FAQs, only the
  calendar) is easier to test, debug, and keep from hallucinating than one giant
  prompt trying to cover every case.
* **Least privilege for tools.** Only the ``calendar_agent`` is given the Google
  Calendar MCP tools. The FAQ path can never accidentally read or write the
  owner's calendar, which keeps the sensitive action behind a single door.
* **Deterministic branches stay deterministic.** Off-topic messages are handled
  by a plain Python node (no LLM call), so we never spend a model call — or risk
  a model going off-script — on something we already know how to answer.

Model choice: every LLM node uses ``gemini-2.5-flash``. Concierge replies and a
one-word classification are latency-sensitive and low-complexity, so Flash gives
the best cost/latency trade-off; the heavier Pro models would add cost and delay
without improving these short, well-scoped tasks.
"""

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


# Constrained output schema for the classifier. Forcing the model to emit one of
# three literal categories (instead of free text) makes routing reliable: the
# router can switch on a known value and never has to parse a prose reply.
class Classification(BaseModel):
    category: Literal["faq", "calendar", "unrelated"] = Field(
        description="The classified category of the user query."
    )


@node
def preprocess_input(ctx: Context, node_input: Any) -> str:
    """Extracts the text of the user message and saves it to state.

    The entrypoint can receive the message in several shapes depending on the
    caller (a raw string from the playground, an ADK ``Content`` object with
    ``parts``, or a plain dict over the A2A/HTTP boundary). We normalize all of
    them to a single string here so downstream nodes only ever deal with text.

    The normalized query is stashed in ``ctx.state["query"]`` so that
    ``router_node`` can forward the *original* wording to the specialist, even
    though the classifier node's own output is just the category label.
    """
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
        # Fallback for any unexpected shape — never crash the workflow on input.
        text = str(node_input)
    ctx.state["query"] = text
    return text


# Intent router. Its only job is to label the message, so it is given a tight
# instruction and the ``Classification`` output schema. Result is written to
# state under ``output_key="classification"`` for the router node to read.
# ``retry_options`` guards against transient model/network errors on this
# critical first hop — if classification fails, nothing downstream can run.
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
    """Routes the workflow based on the classification and forwards the query.

    Two things happen here:

    * ``EventActions(route=category)`` picks the outgoing edge (see the Workflow
      definition below), sending the message to the matching specialist.
    * We set ``output`` back to the *original* guest query (pulled from state),
      not the classifier's label — the specialist needs the real question, not
      the word "faq".

    Defaulting to ``"unrelated"`` is a safe fallback: if the classifier ever
    returns something unexpected, we decline politely rather than misroute a
    message into the calendar path.
    """
    category = node_input.get("category", "unrelated")
    query = ctx.state.get("query", "")
    return Event(output=query, actions=EventActions(route=category))


# FAQ specialist: knowledge-only, intentionally given NO tools. It answers stay
# questions from its instruction and mirrors the guest's language. Keeping it
# tool-free means the FAQ path has zero access to the calendar (least privilege).
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


# Calendar specialist: the only agent with tools. It reaches the owner's real
# Google Calendar through the MCP toolset (see app/tools.py). The instruction
# enforces a strict "read-before-write" contract — always list events and check
# for overlaps BEFORE creating one — so the agent acts on live data and can
# never double-book. This is the human-safety guardrail around the one action
# that has real-world consequences (creating a reservation).
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
    """Politely declines to answer unrelated queries and redirects to stay topics.

    Implemented as a plain node with a fixed bilingual message instead of an LLM
    agent: the response never varies, so a hard-coded reply is cheaper, instant,
    and immune to prompt-injection or off-topic drift. It also keeps the agent
    on-scope, which matters for a customer-facing concierge.
    """
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


# Workflow graph. The first three edges are a linear pipeline (normalize ->
# classify -> route); the last three are conditional edges keyed by ``route``,
# where the router's chosen category selects exactly one specialist branch.
# Each guest turn therefore touches at most two model calls (classify + answer),
# and the "unrelated" branch touches only one.
root_agent = Workflow(
    name="casa_atardecer_workflow",
    edges=[
        ("START", preprocess_input),
        (preprocess_input, classifier_agent),
        (classifier_agent, router_node),
        # Conditional branches — the ``route`` value set by router_node picks one.
        Edge(from_node=router_node, to_node=concierge_faq_agent, route="faq"),
        Edge(from_node=router_node, to_node=calendar_agent, route="calendar"),
        Edge(from_node=router_node, to_node=decline_node, route="unrelated"),
    ],
)


# Exported ADK App consumed by the FastAPI backend (app/fast_api_app.py) and the
# playground. ``root_agent`` is the entrypoint the Runner drives per session.
app = App(
    root_agent=root_agent,
    name="app",
)
