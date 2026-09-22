from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "stm32f407-cicd-template"


def run_command(
    command: list[str],
    working_directory: Path | None = None,
) -> None:
    """Execute a command and stop the build if it fails."""

    printable_command = subprocess.list2cmdline(command)

    print()
    print(f"[CMD] {printable_command}")

    result = subprocess.run(
        command,
        cwd=working_directory,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}: "
            f"{printable_command}"
        )


def require_tool(tool_name: str) -> str:
    """Return the executable path or fail with a clear message."""

    executable = shutil.which(tool_name)

    if executable is None:
        raise FileNotFoundError(
            f"Required tool was not found in PATH: {tool_name}"
        )

    print(f"[TOOL] {tool_name}: {executable}")
    return executable


def verify_file(file_path: Path) -> None:
    """Ensure that an expected build artifact exists."""

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Expected artifact was not generated: {file_path}"
        )

    file_size = file_path.stat().st_size

    print(
        f"[ARTIFACT] {file_path.relative_to(PROJECT_ROOT)} "
        f"({file_size} bytes)"
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the STM32F407 firmware."
    )

    parser.add_argument(
        "--config",
        choices=["Debug", "Release"],
        default="Debug",
        help="Build configuration. Default: Debug",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove previous objects before building.",
    )

    parser.add_argument(
        "--jobs",
        type=int,
        default=os.cpu_count() or 1,
        help="Number of parallel build jobs.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    print("STM32 firmware build")
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Configuration: {args.config}")
    print(f"Parallel jobs: {args.jobs}")

    make = require_tool("make")
    objcopy = require_tool("arm-none-eabi-objcopy")
    size_tool = require_tool("arm-none-eabi-size")
    require_tool("arm-none-eabi-gcc")

    build_directory = PROJECT_ROOT / args.config

    if not build_directory.is_dir():
        raise FileNotFoundError(
            f"Build directory does not exist: {build_directory}"
        )

    makefile = build_directory / "makefile"

    if not makefile.is_file():
        raise FileNotFoundError(
            f"Makefile was not found: {makefile}"
        )

    elf_file = build_directory / f"{PROJECT_NAME}.elf"
    hex_file = build_directory / f"{PROJECT_NAME}.hex"
    bin_file = build_directory / f"{PROJECT_NAME}.bin"
    map_file = build_directory / f"{PROJECT_NAME}.map"
    list_file = build_directory / f"{PROJECT_NAME}.list"

    if args.clean:
        print("\n[STEP] Cleaning previous build")

        run_command(
            [
                make,
                "-C",
                str(build_directory),
                "clean",
            ]
        )

    print("\n[STEP] Building firmware")

    run_command(
        [
            make,
            "-C",
            str(build_directory),
            f"-j{args.jobs}",
            "all",
        ]
    )

    verify_file(elf_file)

    print("\n[STEP] Generating Intel HEX")

    run_command(
        [
            objcopy,
            "-O",
            "ihex",
            str(elf_file),
            str(hex_file),
        ]
    )

    print("\n[STEP] Generating raw binary")

    run_command(
        [
            objcopy,
            "-O",
            "binary",
            str(elf_file),
            str(bin_file),
        ]
    )

    print("\n[STEP] Reporting firmware size")

    run_command(
        [
            size_tool,
            str(elf_file),
        ]
    )

    print("\n[STEP] Validating artifacts")

    for artifact in [
        elf_file,
        hex_file,
        bin_file,
        map_file,
        list_file,
    ]:
        verify_file(artifact)

    print("\n[PASS] Firmware build completed successfully")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[FAIL] Build interrupted by the user", file=sys.stderr)
        sys.exit(130)
    except Exception as error:
        print(f"\n[FAIL] {error}", file=sys.stderr)
        sys.exit(1)