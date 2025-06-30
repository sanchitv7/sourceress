"""Command-line entry point for Sourceress."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click

from sourceress.utils.logging import logger  # noqa: E402 isort: skip
from sourceress import __version__  # noqa: E402 isort: skip
from sourceress.workflows import run_end_to_end  # noqa: E402 isort: skip


@click.command()
@click.option("--jd-file", type=click.Path(exists=True, path_type=Path), help="Path to JD text file.")
@click.option("--output", type=click.Path(path_type=Path), default="output.xlsx", help="Output Excel file.")
@click.version_option(__version__, prog_name="sourceress")
def main(jd_file: Path, output: Path) -> None:  # noqa: D401
    """Run the full pipeline from the CLI."""
    jd_text = jd_file.read_text(encoding="utf-8")
    logger.info("Loaded JD from %s (chars=%d)", jd_file, len(jd_text))
    sys.exit(asyncio.run(run_end_to_end(jd_text, output_path=output)))


if __name__ == "__main__":
    main() 