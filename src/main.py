"""Main entry point for Agent 86."""

import sys
from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .agent import Agent
from .config import get_settings


def setup_logging(log_level: str) -> None:
    """Configure logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )


def display_results(results: dict, console: Console) -> None:
    """Display agent results in a nice format.
    
    Args:
        results: Results dictionary from agent
        console: Rich console
    """
    # Display goal
    console.print(Panel(f"[bold cyan]Goal:[/bold cyan] {results['goal']}", expand=False))
    console.print()
    
    # Display tasks
    task_table = Table(title="Tasks", show_header=True, header_style="bold magenta")
    task_table.add_column("ID", style="dim", width=6)
    task_table.add_column("Description")
    task_table.add_column("Status", justify="center")
    
    for task in results["tasks"]:
        status_color = {
            "completed": "green",
            "in-progress": "yellow",
            "pending": "cyan",
            "failed": "red"
        }.get(task["status"], "white")
        
        task_table.add_row(
            str(task["id"]),
            task["description"],
            f"[{status_color}]{task['status']}[/{status_color}]"
        )
    
    console.print(task_table)
    console.print()
    
    # Display reasoning steps
    if results["reasoning_steps"]:
        console.print("[bold yellow]Reasoning Steps:[/bold yellow]")
        for i, step in enumerate(results["reasoning_steps"][-5:], 1):  # Last 5
            console.print(f"  {i}. [cyan]Thought:[/cyan] {step['thought']}")
            if step.get("action"):
                console.print(f"     [green]Action:[/green] {step['action']}")
            if step.get("observation"):
                obs = step["observation"][:100] + "..." if len(step["observation"]) > 100 else step["observation"]
                console.print(f"     [yellow]Observation:[/yellow] {obs}")
            console.print()
    
    # Display summary
    success_icon = "✓" if results["success"] else "✗"
    success_color = "green" if results["success"] else "red"
    console.print(Panel(
        f"[{success_color}]{success_icon} Status:[/{success_color}] {'Success' if results['success'] else 'Failed'}\n"
        f"[cyan]Iterations:[/cyan] {results['iterations']}",
        title="Summary",
        expand=False
    ))


def main() -> None:
    """Run the agent."""
    # Load settings
    settings = get_settings()
    setup_logging(settings.log_level)
    
    console = Console()
    
    # Display banner
    console.print(Panel(
        "[bold cyan]Agent 86[/bold cyan]\n"
        "A powerful AI agent using llama.cpp and guidance-ai",
        expand=False
    ))
    console.print()
    
    # Initialize agent
    try:
        agent = Agent(settings)
        agent.load()
    except Exception as e:
        console.print(f"[bold red]Error loading agent:[/bold red] {e}")
        logger.exception("Failed to load agent")
        sys.exit(1)
    
    # Get goal from user
    console.print("[bold green]Enter your goal (or 'quit' to exit):[/bold green]")
    goal = input("> ").strip()
    
    if goal.lower() in ["quit", "exit", "q"]:
        console.print("[yellow]Goodbye![/yellow]")
        return
    
    if not goal:
        console.print("[red]No goal provided. Exiting.[/red]")
        return
    
    # Run agent
    console.print("\n[bold yellow]Running agent...[/bold yellow]\n")
    
    try:
        results = agent.run(goal)
        display_results(results, console)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error during execution:[/bold red] {e}")
        logger.exception("Agent execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
