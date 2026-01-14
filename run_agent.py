#!/usr/bin/env python
"""
Run Agent 86 - Quick launcher script.

Usage:
    python run_agent.py [goal]
    
Examples:
    python run_agent.py
    python run_agent.py "Find Python files in current directory"
    python run_agent.py "Check system information and list running processes"
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import Agent
from src.config import Settings


def main():
    """Run the agent with optional goal from command line."""
    # Get goal from command line or use default
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
    else:
        print("\n=== Agent 86 ===")
        print("\nEnter your goal (or press Enter for default):")
        goal = input("> ").strip()
        
        if not goal:
            goal = "List all Python files in the current directory"
            print(f"\nUsing default goal: {goal}")
    
    print(f"\n[Goal] {goal}")
    print("=" * 60)
    
    # Load settings and create agent
    settings = Settings()
    agent = Agent(settings)
    agent.load()  # Load LLM model
    
    # Run agent
    try:
        result = agent.run(goal)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Agent completed!")
        print("=" * 60)
        
        if result:
            print(f"\nFinal Result:\n{result}")
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Agent interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
