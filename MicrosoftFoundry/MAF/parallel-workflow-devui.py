"""
Parallel vacation-planner workflow with Microsoft Agent Framework,
Azure AI Foundry and DevUI.
"""

import asyncio
import inspect
import logging
import os
from typing import Any

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from agent_framework import (
    Agent,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowViz,
    handler,
)
from agent_framework.devui import serve
from agent_framework.foundry import FoundryChatClient


load_dotenv()

PROJECT_ENDPOINT = os.getenv("AI_FOUNDRY_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME")

if not PROJECT_ENDPOINT:
    raise ValueError("AI_FOUNDRY_PROJECT_ENDPOINT saknas i .env-filen.")

if not MODEL_DEPLOYMENT_NAME:
    raise ValueError("AI_FOUNDRY_DEPLOYMENT_NAME saknas i .env-filen.")


async def extract_text(response: Any) -> str:
    """Extract readable text from an Agent Framework response."""

    if hasattr(response, "get_final_response"):
        response = await response.get_final_response()

    for attribute in ("text", "content"):
        value = getattr(response, attribute, None)
        if value:
            return str(value)

    message = getattr(response, "message", None)
    if message:
        for attribute in ("text", "content"):
            value = getattr(message, attribute, None)
            if value:
                return str(value)
        return str(message)

    return str(response)


async def close_resource(resource: Any) -> None:
    """Close both synchronous and asynchronous resources safely."""

    close = getattr(resource, "close", None)

    if close is None:
        return

    result = close()

    if inspect.isawaitable(result):
        await result


async def create_agent(
    name: str,
    instructions: str,
) -> tuple[Agent, FoundryChatClient, DefaultAzureCredential]:
    """Create one Foundry-backed MAF agent."""

    credential = DefaultAzureCredential()

    client = FoundryChatClient(
        project_endpoint=PROJECT_ENDPOINT,
        model=MODEL_DEPLOYMENT_NAME,
        credential=credential,
    )

    agent = Agent(
        name=name,
        instructions=instructions,
        client=client,
    )

    print(f"{name} created.")

    return agent, client, credential


class LocationSelectorExecutor(Executor):
    """Chooses a suitable destination from the travel request."""

    def __init__(self, agent: Agent, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(
        self,
        user_query: str,
        ctx: WorkflowContext[str],
    ) -> None:
        prompt = f"""
Choose one vacation destination that best fits this request:

{user_query}

Return a concise destination recommendation with country or region
and a short reason.
"""

        response = await self.agent.run(prompt)
        location = await extract_text(response)

        print("\n--- Location selection ---\n")
        print(location)

        await ctx.send_message(location)


class DestinationRecommenderExecutor(Executor):
    """Suggests history, culture and experiences for the destination."""

    def __init__(self, agent: Agent, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(
        self,
        location: str,
        ctx: WorkflowContext[str],
    ) -> None:
        prompt = f"""
Recommend historical and cultural experiences for this destination:

{location}

Include important sites, a suggested trip duration and practical considerations.
"""

        response = await self.agent.run(prompt)
        result = await extract_text(response)

        print("\n--- Destination recommendations ---\n")
        print(result)

        await ctx.send_message(result)


class WeatherExecutor(Executor):
    """Provides weather and seasonal travel advice."""

    def __init__(self, agent: Agent, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(
        self,
        location: str,
        ctx: WorkflowContext[str],
    ) -> None:
        prompt = f"""
Provide weather and seasonal travel guidance for this destination:

{location}

The traveller prefers warm weather. Include the best months to visit,
typical climate and packing advice.
"""

        response = await self.agent.run(prompt)
        result = await extract_text(response)

        print("\n--- Weather guidance ---\n")
        print(result)

        await ctx.send_message(result)


class CuisineExecutor(Executor):
    """Suggests local food experiences."""

    def __init__(self, agent: Agent, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(
        self,
        location: str,
        ctx: WorkflowContext[str],
    ) -> None:
        prompt = f"""
Recommend local food experiences for this destination:

{location}

Include popular dishes, food markets or neighbourhoods, and practical food advice.
"""

        response = await self.agent.run(prompt)
        result = await extract_text(response)

        print("\n--- Cuisine guidance ---\n")
        print(result)

        await ctx.send_message(result)


class ItineraryPlannerExecutor(Executor):
    """Combines parallel recommendations into one final itinerary."""

    def __init__(self, agent: Agent, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(
        self,
        results: list[str],
        ctx: WorkflowContext[str],
    ) -> None:
        expert_inputs = "\n\n".join(
            f"--- Expert input {index + 1} ---\n{result}"
            for index, result in enumerate(results)
        )

        prompt = f"""
Create a practical and engaging five-day vacation itinerary based on the
following expert inputs:

{expert_inputs}

Include:
- Destination overview
- Recommended travel period
- Day-by-day plan
- Historical sites and cultural activities
- Local food recommendations
- Weather and packing advice
- Short practical checklist

Do not invent facts absent from the expert inputs.
"""

        response = await self.agent.run(prompt)
        itinerary = await extract_text(response)

        print("\n--- Final itinerary ---\n")
        print(itinerary)

        await ctx.yield_output(itinerary)


async def build_workflow() -> tuple[Any, list[Any]]:
    location_agent, location_client, location_credential = await create_agent(
        "Location-Picker-Agent",
        "You are a travel destination specialist who selects one suitable destination.",
    )

    destination_agent, destination_client, destination_credential = (
        await create_agent(
            "Destination-Recommender-Agent",
            "You are a travel expert focused on historical and cultural attractions.",
        )
    )

    weather_agent, weather_client, weather_credential = await create_agent(
        "Weather-Agent",
        "You are a travel-weather expert who provides useful seasonal guidance.",
    )

    cuisine_agent, cuisine_client, cuisine_credential = await create_agent(
        "Cuisine-Suggestion-Agent",
        "You are a culinary travel expert who recommends local food experiences.",
    )

    itinerary_agent, itinerary_client, itinerary_credential = await create_agent(
        "Itinerary-Planner-Agent",
        "You combine expert travel advice into coherent and realistic itineraries.",
    )

    location = LocationSelectorExecutor(
        agent=location_agent,
        id="location_selector",
    )

    destination = DestinationRecommenderExecutor(
        agent=destination_agent,
        id="destination_recommender",
    )

    weather = WeatherExecutor(
        agent=weather_agent,
        id="weather",
    )

    cuisine = CuisineExecutor(
        agent=cuisine_agent,
        id="cuisine",
    )

    itinerary = ItineraryPlannerExecutor(
        agent=itinerary_agent,
        id="itinerary_planner",
    )

    workflow = (
        WorkflowBuilder(
            name="Parallel Vacation Planner",
            description=(
                "Selects a destination, gathers travel advice in parallel "
                "and produces an itinerary."
            ),
            start_executor=location,
        )
        .add_fan_out_edges(
            location,
            [destination, weather, cuisine],
        )
        .add_fan_in_edges(
            [destination, weather, cuisine],
            itinerary,
        )
        .build()
    )

    print("\n--- Mermaid diagram ---\n")
    print(WorkflowViz(workflow).to_mermaid())

    resources = [
        location_agent,
        location_client,
        location_credential,
        destination_agent,
        destination_client,
        destination_credential,
        weather_agent,
        weather_client,
        weather_credential,
        cuisine_agent,
        cuisine_client,
        cuisine_credential,
        itinerary_agent,
        itinerary_client,
        itinerary_credential,
    ]

    return workflow, resources


async def cleanup(resources: list[Any]) -> None:
    """Close agents, Foundry clients and Azure credentials."""

    for resource in resources:
        try:
            await close_resource(resource)
        except Exception as error:
            print(f"Cleanup warning: {error}")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    workflow, resources = asyncio.run(build_workflow())

    print("\nStarting DevUI at http://127.0.0.1:8090")

    try:
        serve(
            entities=[workflow],
            port=8090,
            auto_open=True
        )
    except KeyboardInterrupt:
        print("\nDevUI stopped.")
    finally:
        asyncio.run(cleanup(resources))


if __name__ == "__main__":
    main()