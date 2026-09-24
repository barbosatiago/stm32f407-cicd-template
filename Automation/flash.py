from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "stm32f407-cicd-template"


def run_command(command: list[str]) -> None:
    printable_command = subprocess.list2cmdline(command)

    print()
    print(f"[CMD] {printable_command}")

    result = subprocess.run(
        command,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}: "
            f"{printable_command}"
        )


def find_programmer() -> str:
    executable = shutil.which("STM32_Programmer_CLI")
    if executable:
        print(f"[TOOL] STM32 Programmer: {executable}")
        return executable

    executable = shutil.which("STM32_Programmer_CLI.exe")
    if executable:
        print(f"[TOOL] STM32 Programmer: {executable}")
        return executable

    configured_path = os.getenv("STM32_PROGRAMMER_CLI")
    if configured_path:
        path = Path(configured_path)

        if path.is_file():
            print(f"[TOOL] STM32 Programmer: {path}")
            return str(path)

        raise FileNotFoundError(
            "STM32_PROGRAMMER_CLI points to a file that does not exist: "
            f"{path}"
        )

    raise FileNotFoundError(
        "STM32_Programmer_CLI was not found. "
        "Add its directory to PATH or define STM32_PROGRAMMER_CLI."
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Program the STM32F407 firmware through ST-LINK."
    )

    parser.add_argument(
        "--config",
        choices=["Debug", "Release"],
        default="Debug",
        help="Build configuration containing the firmware image.",
    )

    parser.add_argument(
        "--image",
        type=Path,
        help="Custom ELF, HEX or BIN image.",
    )

    parser.add_argument(
        "--erase-all",
        action="store_true",
        help="Perform a full Flash erase before programming.",
    )

    parser.add_argument(
        "--under-reset",
        action="store_true",
        help="Connect to the target under hardware reset.",
    )

    parser.add_argument(
        "--serial-number",
        help="Select a specific ST-LINK by serial number.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    programmer = find_programmer()

    if args.image:
        image = args.image.resolve()
    else:
        image = (
            PROJECT_ROOT
            / args.config
            / f"{PROJECT_NAME}.hex"
        )

    if not image.is_file():
        raise FileNotFoundError(
            f"Firmware image was not found: {image}\n"
            "Run Automation/build.py before flashing."
        )

    supported_formats = {".elf", ".hex", ".bin"}

    if image.suffix.lower() not in supported_formats:
        raise ValueError(
            f"Unsupported firmware format: {image.suffix}"
        )

    connection = ["port=SWD"]

    if args.under_reset:
        connection.extend(
            [
                "mode=UR",
                "reset=HWrst",
            ]
        )

    if args.serial_number:
        connection.append(f"sn={args.serial_number}")

    print("STM32 firmware flash")
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Image        : {image}")
    print(f"Image size   : {image.stat().st_size} bytes")
    print(f"Erase all    : {args.erase_all}")
    print(f"Under reset  : {args.under_reset}")

    print("\n[STEP] Detecting connected ST-LINK probes")

    run_command(
        [
            programmer,
            "-l",
            "stlink",
        ]
    )

    if args.erase_all:
        print("\n[STEP] Performing full Flash erase")

        run_command(
            [
                programmer,
                "-c",
                *connection,
                "-e",
                "all",
            ]
        )

    print("\n[STEP] Programming and verifying firmware")

    command = [
        programmer,
        "-c",
        *connection,
        "-w",
        str(image),
    ]

    if image.suffix.lower() == ".bin":
        command.append("0x08000000")

    command.extend(
        [
            "-v",
            "-rst",
        ]
    )

    run_command(command)

    print("\n[PASS] Firmware programmed and verified successfully")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(
            "\n[FAIL] Flash operation interrupted by the user",
            file=sys.stderr,
        )
        sys.exit(130)
    except Exception as error:
        print(f"\n[FAIL] {error}", file=sys.stderr)
        sys.exit(1)