# to run - uv run python devui.py

import os
from dotenv import load_dotenv
from collections.abc import Awaitable, Callable
from typing import Annotated

from agent_framework import (
    ChatAgent,
    ChatContext,
    ChatMessage,
    ChatResponse,
    FunctionInvocationContext,
    Role,
    WorkflowBuilder,
    chat_middleware,
    function_middleware,
)
from agent_framework.azure import AzureOpenAIChatClient

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")


@chat_middleware
async def security_filter_middleware(
    context: ChatContext,
    next: Callable[[ChatContext], Awaitable[None]],
) -> None:
    """Chat middleware that blocks requests containing sensitive information."""
    # Block requests with sensitive information
    blocked_terms = ["password", "secret", "api_key", "token"]

    for message in context.messages:
        if message.text:
            message_lower = message.text.lower()
            for term in blocked_terms:
                if term in message_lower:
                    # Override the response without calling the LLM
                    context.result = ChatResponse(
                        messages=[
                            ChatMessage(
                                role=Role.ASSISTANT,
                                text=(
                                    "I cannot process requests containing sensitive information. "
                                    "Please rephrase your question without including passwords, secrets, "
                                    "or other sensitive data."
                                ),
                            )
                        ]
                    )
                    return

    await next(context)


@function_middleware
async def atlantis_location_filter_middleware(
    context: FunctionInvocationContext,
    next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """Function middleware that blocks weather requests for Atlantis."""
    # Check if location parameter is "atlantis"
    location = getattr(context.arguments, "location", None)
    if location and location.lower() == "atlantis":
        context.result = (
            "Blocked! Hold up right there!! Tell the user that "
            "'Atlantis is a special place, we must never ask about the weather there!!'"
        )
        context.terminate = True
        return

    await next(context)


def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temperature = 53
    return f"The weather in {location} is {conditions[0]} with a high of {temperature}°C."


def get_forecast(
    location: Annotated[str, "The location to get the forecast for."],
    days: Annotated[int, "Number of days for forecast"] = 3,
) -> str:
    """Get weather forecast for multiple days."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    forecast: list[str] = []

    for day in range(1, days + 1):
        condition = conditions[0]
        temp = 53
        forecast.append(f"Day {day}: {condition}, {temp}°C")

    return f"Weather forecast for {location}:\n" + "\n".join(forecast)

client = AzureOpenAIChatClient(
        endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
        deployment_name=deployment,
    )
# Agent instance following Agent Framework conventions
agent = ChatAgent(
    name="AzureWeatherAgent",
    description="A helpful agent that provides weather information and forecasts",
    instructions="""
    You are a weather assistant. You can provide current weather information
    and forecasts for any location. Always be helpful and provide detailed
    weather information when asked.
    """,
    chat_client=client,
    tools=[get_weather, get_forecast],
    middleware=[security_filter_middleware, atlantis_location_filter_middleware],
)

analyst_agent = client.create_agent(
    instructions=(
        "You are a business analyst. Draft a short business case based on the provided idea. "
    ),
    name="analyst",
)

finance_agent = client.create_agent(
    instructions=(
        "You are a finance expert. Review the business case and highlight any financial risks or constraints."
    ),
    name="finance",
)

approval_agent = client.create_agent(
    instructions=(
        "You are a senior manager. Decide whether to approve the business case based on strategic alignment. "
        "Respond with 'Approved' or 'Needs Revision' and provide reasoning."
    ),
    name="approval",
)


workflow = (
    WorkflowBuilder()
    .set_start_executor(analyst_agent)
    .add_edge(analyst_agent, finance_agent)
    .add_edge(finance_agent, approval_agent)
    .build()
)


def main():
    """Launch the Azure weather agent in DevUI."""
    import logging

    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Azure Weather Agent")
    logger.info("Available at: http://localhost:8090")
    logger.info("Entity ID: agent_AzureWeatherAgent")

    # Launch server with the agent
    serve(entities=[workflow], port=8090, auto_open=True)


if __name__ == "__main__":
    main()