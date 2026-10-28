# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

import argparse
from pathlib import Path
import shutil
import subprocess


def drive_path(path):
    # Escape commas used as separators in QEMU drive options.
    return str(path.resolve()).replace(",", ",,")


def main():
    parser = argparse.ArgumentParser(
        description="Boot Ferrite using QEMU, TCG, and VirtIO devices."
    )
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument(
        "--firmware-code",
        type=Path,
        default=Path("/usr/share/edk2/x64/OVMF_CODE.4m.fd"),
    )
    parser.add_argument(
        "--firmware-vars",
        type=Path,
        default=Path("/usr/share/edk2/x64/OVMF_VARS.4m.fd"),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Pause at startup and expose GDB on localhost:1234.",
    )
    args = parser.parse_args()

    qemu = shutil.which("qemu-system-x86_64")
    if qemu is None:
        parser.error("Required tool not found: qemu-system-x86_64")

    for source in (args.image, args.firmware_code, args.firmware_vars):
        if not source.is_file():
            parser.error(f"Input file not found: {source}")

    variables = args.image.resolve().parent / "OVMF_VARS.fd"

    if not variables.exists():
        shutil.copyfile(args.firmware_vars, variables)

    command = [
        qemu,

        # Platform and CPU topology: 2 cores, 4 logical CPUs.
        "-machine", "q35,usb=off,i8042=off,sata=off",
        "-accel", "tcg,thread=multi",
        "-cpu", "max",
        "-smp", "4,sockets=1,cores=4,threads=1",
        "-m", "8192M",

        # Disable automatically added peripherals.
        "-nodefaults",

        # UEFI firmware with disposable variable storage.
        "-drive",
        (
            "if=pflash,format=raw,readonly=on,"
            f"file={drive_path(args.firmware_code)}"
        ),
        "-drive",
        f"if=pflash,format=raw,file={drive_path(variables)}",

        # VirtIO block storage with disposable disk writes.
        "-drive",
        (
            "if=none,id=osdisk,format=qcow2,snapshot=on,"
            f"file={drive_path(args.image)}"
        ),
        "-device", "virtio-blk-pci,drive=osdisk,bootindex=1",

        # VirtIO GPU with an explicit graphical window.
        "-device", "virtio-gpu-pci",
        "-display", "gtk,gl=off",

        # VirtIO input devices; no USB or PS/2 input.
        "-device", "virtio-keyboard-pci",
        "-device", "virtio-mouse-pci",

        # VirtIO network device with user-mode networking.
        "-netdev", "user,id=net0",
        "-device", "virtio-net-pci,netdev=net0",

        # VirtIO entropy source.
        "-object", "rng-random,id=rng0,filename=/dev/urandom",
        "-device", "virtio-rng-pci,rng=rng0",

        # Pipe all COM1 data into the terminal.
        "-serial", "stdio",

        # Keep failures visible instead of restarting or exiting.
        "-monitor", "none",
        "-no-reboot",
        "-no-shutdown",
    ]

    if args.debug:
        command.extend([
            "-S",
            "-gdb", "tcp:127.0.0.1:1234",
        ])

    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
