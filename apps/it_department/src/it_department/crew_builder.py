from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import write_markdown_artifact
from .config import AppConfig
from .llm_factory import create_llm, get_role_models
from .models import RoleArtifact
from .runtime_env import prepare_crewai_runtime


def build_agents(config: AppConfig) -> dict[str, Any]:
    prepare_crewai_runtime(config.project_root)
    from crewai import Agent

    models = get_role_models(config)
    return {
        "pm": Agent(
            role="PM Manager",
            goal="Coordinate the IT department and deliver a consistent final execution package.",
            backstory=(
                "You are the delivery manager. You decompose work, align team outputs, and keep "
                "the whole package cohesive and shippable."
            ),
            llm=create_llm(config, models.pm),
            verbose=True,
            allow_delegation=True,
        ),
        "ba": Agent(
            role="Business Analyst",
            goal="Turn product requests into implementation-ready business artifacts.",
            backstory=(
                "You specialize in structured discovery, backlog shaping, user stories, and "
                "acceptance criteria."
            ),
            llm=create_llm(config, models.ba),
            verbose=True,
        ),
        "backend": Agent(
            role="Backend Architect",
            goal="Design backend contracts, entities, and service boundaries from approved business scope.",
            backstory="You focus on APIs, validation, domain modeling, and system reliability.",
            llm=create_llm(config, models.backend),
            verbose=True,
        ),
        "frontend": Agent(
            role="Frontend Lead",
            goal="Translate product and backend context into production-quality frontend implementation guidance.",
            backstory=(
                "You own user flows, interface structure, state dependencies, and production-grade "
                "delivery decisions for a Next.js app."
            ),
            llm=create_llm(config, models.frontend),
            verbose=True,
        ),
        "qc": Agent(
            role="Quality Controller",
            goal="Produce release-focused test scenarios and coverage recommendations.",
            backstory="You think in regression risks, validation matrices, and release confidence.",
            llm=create_llm(config, models.qc),
            verbose=True,
        ),
    }


def build_crew(config: AppConfig, product_request: str) -> Any:
    prepare_crewai_runtime(config.project_root)
    from crewai import Crew, Process, Task

    agents = build_agents(config)
    tasks = [
        Task(
            description=(
                "Create a business analysis package for this product request:\n"
                f"{product_request}\n\n"
                "Return Markdown with these sections: Product Objective, Scope, Out of Scope, "
                "Assumptions, User Stories, Acceptance Criteria, Priority Order, Open Questions and Risks."
            ),
            expected_output="A structured Markdown business artifact.",
            agent=agents["ba"],
        ),
        Task(
            description=(
                "Based on the approved business analysis, create a backend design package with "
                "API contract, entities, service boundaries, validation rules, non-functional "
                "considerations, and rollout notes."
            ),
            expected_output="A structured Markdown backend solution design.",
            agent=agents["backend"],
        ),
        Task(
            description=(
                "Create frontend implementation guidance for a Next.js App Router application. "
                "Return Markdown with route structure, component plan, state/data dependencies, "
                "and production delivery notes for the frontend generator."
            ),
            expected_output="A structured Markdown frontend implementation package.",
            agent=agents["frontend"],
        ),
        Task(
            description=(
                "Create a QC package covering smoke tests, regression checks, acceptance mapping, "
                "and release risks based on the business, backend, and frontend outputs."
            ),
            expected_output="A structured Markdown QC plan.",
            agent=agents["qc"],
        ),
        Task(
            description=(
                "Summarize the run as PM. Provide an executive delivery summary, sequencing, key "
                "dependencies, and recommended next actions."
            ),
            expected_output="A concise Markdown PM delivery summary.",
            agent=agents["pm"],
        ),
    ]
    return Crew(
        agents=[agents["ba"], agents["backend"], agents["frontend"], agents["qc"]],
        tasks=tasks,
        process=Process.hierarchical,
        manager_agent=agents["pm"],
        verbose=True,
    )


def persist_role_output(
    config: AppConfig,
    run_id: str,
    role: str,
    title: str,
    output: str,
) -> RoleArtifact:
    summary = _summarize(output)
    return write_markdown_artifact(config.outputs_dir, run_id, role, title, output, summary)


def _summarize(markdown: str) -> str:
    for line in markdown.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line[:180]
    return "Structured artifact generated."
