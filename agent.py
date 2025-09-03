# agent.py
import argparse
import subprocess
import sys
import time

MAX_RETRIES = 3

def run_pytest() -> bool:
    """Run pytest and return True if tests pass, False otherwise."""
    try:
        result = subprocess.run(
            ["pytest", "-q"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running pytest: {e}")
        return False

def agent(target: str):
    """
    Main agent loop.
    Shows autonomy via retry attempts and (simulated) self-debug,
    but does not overwrite the stable parser.
    """
    print(f"🤖 Starting agent for target: {target}\n")

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"Attempt {attempt}: running pytest...\n")
        success = run_pytest()

        if success:
            print("✅ Parser works! All tests passed.")
            return

        # If tests fail, simulate what the agent would do
        print("❌ Tests failed.")
        if attempt < MAX_RETRIES:
            print("🔄 Self-debug: would regenerate parser with Gemini (skipped to preserve stable version).")
            time.sleep(1)  # small delay to simulate work
        else:
            print("⚠️ Failed after retries. Please check parser manually.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Target bank name (e.g., icici)")
    args = parser.parse_args()
    agent(args.target)

if __name__ == "__main__":
    main()
