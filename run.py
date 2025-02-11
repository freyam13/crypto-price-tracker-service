import subprocess
import sys
from pathlib import Path

import click


@click.command()
@click.option("--api-only", is_flag=True, help="Run only the API service")
@click.option("--ui-only", is_flag=True, help="Run only the UI service")
def run(api_only: bool, ui_only: bool):
    if api_only and ui_only:
        click.echo("Cannot specify both --api-only and --ui-only")
        sys.exit(1)

    if not ui_only:
        api_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "src.api.routes:app",
                "--host",
                "localhost",
                "--port",
                "8000",
                "--reload",
            ],
            env={"PYTHONPATH": str(Path(__file__).parent.parent)},
        )

    if not api_only:
        ui_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "src/ui/streamlit_app.py"]
        )

    try:
        if not ui_only:
            api_process.wait()

        if not api_only:
            ui_process.wait()

    except KeyboardInterrupt:
        if not ui_only:
            api_process.terminate()

        if not api_only:
            ui_process.terminate()


if __name__ == "__main__":
    run()
