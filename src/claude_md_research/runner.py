"""Execute Claude CLI sessions and capture output."""

import subprocess
import shlex
from dataclasses import dataclass


@dataclass
class RunResult:
    """Result of a Claude session."""

    success: bool
    output: str
    error: str
    working_dir: str
    prompt: str
    duration_seconds: float = 0.0


def run_claude_session(
    working_dir: str,
    prompt: str,
    timeout: int = 60,
) -> RunResult:
    """
    Run Claude CLI with a prompt and capture output.

    Uses: claude --print --prompt "..."
    """
    import time

    cmd = ["claude", "--print", "--prompt", prompt]

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        duration = time.time() - start_time

        return RunResult(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr,
            working_dir=working_dir,
            prompt=prompt,
            duration_seconds=duration,
        )

    except subprocess.TimeoutExpired:
        return RunResult(
            success=False,
            output="",
            error=f"Timeout after {timeout} seconds",
            working_dir=working_dir,
            prompt=prompt,
            duration_seconds=timeout,
        )
    except FileNotFoundError:
        return RunResult(
            success=False,
            output="",
            error="Claude CLI not found. Is it installed?",
            working_dir=working_dir,
            prompt=prompt,
            duration_seconds=0.0,
        )
    except Exception as e:
        return RunResult(
            success=False,
            output="",
            error=str(e),
            working_dir=working_dir,
            prompt=prompt,
            duration_seconds=time.time() - start_time,
        )
