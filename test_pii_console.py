import asyncio

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


async def main():
    # Creamos una sesión en memoria
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        user_id="console_user", app_name="app"
    )
    runner = Runner(agent=root_agent, session_service=session_service, app_name="app")

    # Tu consulta exacta con datos personales
    query = (
        "Hola, mi email es guest@test.com, mi teléfono es +34 600 000 000 y "
        "mi tarjeta de crédito es 4111-2222-3333-4444. ¿Se puede reservar para el 10 al 17 de septiembre de 2026?"
    )

    print("\n===============================================")
    print("1. ENVIANDO CONSULTA ORIGINAL:")
    print(f'   "{query}"')
    print("===============================================\n")

    message = types.Content(role="user", parts=[types.Part.from_text(text=query)])

    # Ejecutamos el agente
    events = []
    async for event in runner.run_async(
        new_message=message,
        user_id="console_user",
        session_id=session.id,
        run_config=RunConfig(streaming_mode=StreamingMode.NONE),
    ):
        events.append(event)

    # Obtenemos el estado actualizado
    updated_session = await session_service.get_session(
        app_name="app", user_id="console_user", session_id=session.id
    )

    # Extraemos la respuesta textual
    response_text = ""
    for event in events:
        if event.content and event.content.parts:
            response_text += "".join(p.text for p in event.content.parts if p.text)

    print("===============================================")
    print("2. RESULTADO TRAS EL CHEQUEO DE SEGURIDAD:")
    print("===============================================")
    print("🔎 Consulta Sanitizada (ctx.state['query']):")
    print(f"   -> {updated_session.state.get('query')}\n")

    print("🏷️  Categorías Redactadas (ctx.state['redacted_categories']):")
    print(f"   -> {updated_session.state.get('redacted_categories')}\n")

    print("💬 Respuesta final del Concierge:")
    print(f"   -> {response_text}")
    print("===============================================\n")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    asyncio.run(main())
