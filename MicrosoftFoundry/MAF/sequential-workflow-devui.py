"""
Sequential workflow with Microsoft Agent Framework, Azure AI Foundry and DevUI.

Run:
    python sequential_workflow.py
"""

import asyncio
import inspect
import logging
import os
from typing import Any

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential

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


async def get_response_text(response: Any) -> str:
    """Extract readable text from an MAF agent response."""

    if hasattr(response, "get_final_response"):
        response = await response.get_final_response()

    if hasattr(response, "text") and response.text:
        return str(response.text)

    if hasattr(response, "content") and response.content:
        return str(response.content)

    return str(response)


async def close_resource(resource: Any) -> None:
    """Close a synchronous or asynchronous resource safely."""

    close_method = getattr(resource, "close", None)

    if close_method is None:
        return

    result = close_method()

    if inspect.isawaitable(result):
        await result


async def create_agent(
    agent_name: str,
    agent_instructions: str,
) -> tuple[Agent, DefaultAzureCredential]:
    """Create an Azure AI Foundry-backed agent."""

    credential = DefaultAzureCredential()

    chat_client = FoundryChatClient(
        project_endpoint=PROJECT_ENDPOINT,
        model=MODEL_DEPLOYMENT_NAME,
        credential=credential,
    )

    agent = Agent(
        name=agent_name,
        instructions=agent_instructions,
        client=chat_client,
    )

    print(f"{agent_name} created successfully.")

    return agent, credential


class ResearcherExecutor(Executor):
    """Researches the incoming topic and sends notes to the writer."""

    def __init__(self, agent: Agent, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(
        self,
        query: str,
        ctx: WorkflowContext[str],
    ) -> None:
        prompt = f"""
            Research this topic:

            {query}

            Provide concise, structured research notes for an essay writer.
            Include benefits, risks, examples and nuanced perspectives.
            """

        response = await self.agent.run(prompt)
        research_text = await get_response_text(response)

        print("\n--- Researcher output ---\n")
        print(research_text)

        await ctx.send_message(research_text)


class WriterExecutor(Executor):
    """Writes the final essay from the research notes."""

    def __init__(self, agent: Agent, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(
        self,
        research_data: str,
        ctx: WorkflowContext[str],
    ) -> None:
        prompt = f"""
            Write a balanced and engaging essay using the research notes below.

            Research notes:
            {research_data}

            Use a title, introduction, clear paragraphs and conclusion.
            Do not invent facts that are absent from the research notes.
            """

        response = await self.agent.run(prompt)
        essay_text = await get_response_text(response)

        print("\n--- Writer output ---\n")
        print(essay_text)

        await ctx.yield_output(essay_text)


async def build_workflow() -> tuple[Any, list[Any]]:
    researcher_agent, researcher_credential = await create_agent(
        agent_name="Researcher-Agent",
        agent_instructions=(
            "You are a careful and knowledgeable researcher. "
            "Provide accurate, balanced and concise research notes."
        ),
    )

    writer_agent, writer_credential = await create_agent(
        agent_name="Writer-Agent",
        agent_instructions=(
            "You are a skilled essay writer. Turn supplied research notes "
            "into a clear, coherent and engaging essay."
        ),
    )

    researcher_executor = ResearcherExecutor(
        agent=researcher_agent,
        id="researcher_executor",
    )

    writer_executor = WriterExecutor(
        agent=writer_agent,
        id="writer_executor",
    )

    workflow = (
        WorkflowBuilder(
            name="Sequential Research and Writing Workflow",
            description="Researches a topic and writes an essay.",
            start_executor=researcher_executor,
        )
        .add_edge(researcher_executor, writer_executor)
        .build()
    )

    viz = WorkflowViz(workflow)

    print("\n--- Mermaid diagram ---\n")
    print(viz.to_mermaid())

    resources = [
        researcher_agent,
        writer_agent,
        researcher_credential,
        writer_credential,
    ]

    return workflow, resources


async def cleanup(resources: list[Any]) -> None:
    """Closes agents and Azure credentials."""

    print("\nCleaning up resources...")

    for resource in resources:
        try:
            await close_resource(resource)
        except Exception as error:
            print(f"Cleanup warning: {error}")

    print("Cleanup completed.")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    print("Building workflow...")
    workflow, resources = asyncio.run(build_workflow())

    print("\nStarting DevUI...")
    print("Open: http://localhost:8090")

    try:
        serve(
            entities=[workflow],
            port=8090,
            auto_open=True,
        )
    except KeyboardInterrupt:
        print("\nDevUI stopped by user.")
    finally:
        asyncio.run(cleanup(resources))


if __name__ == "__main__":
    main()