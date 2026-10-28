# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

MIB = 1024 * 1024
SECTOR_SIZE = 512

ESP_START = 2048
ESP_SIZE = 64 * MIB
DISK_SIZE = 68 * MIB


def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Create a bootable Ferrite qcow2 image."
    )
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--bootloader", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    for tool in ("sgdisk", "mkfs.fat", "mmd", "mcopy", "qemu-img"):
        if shutil.which(tool) is None:
            parser.error(f"Required tool not found: {tool}")

    for source in (args.kernel, args.bootloader, args.config):
        if not source.is_file():
            parser.error(f"Input file not found: {source}")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    # Keep temporary files on the same filesystem as the final output.
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        temporary = Path(temporary)
        disk = temporary / "disk.img"
        esp = temporary / "esp.img"
        qcow2 = temporary / "disk.qcow2"

        # Create the raw disk and its GPT partition table.
        with disk.open("wb") as stream:
            stream.truncate(DISK_SIZE)

        esp_sectors = ESP_SIZE // SECTOR_SIZE
        esp_end = ESP_START + esp_sectors - 1

        run(
            "sgdisk",
            "--clear",
            f"--new=1:{ESP_START}:{esp_end}",
            "--typecode=1:ef00",
            "--change-name=1:EFI System Partition",
            disk,
        )

        # Format a separate FAT32 EFI System Partition.
        with esp.open("wb") as stream:
            stream.truncate(ESP_SIZE)

        run("mkfs.fat", "-F", "32", "-n", "FERRITE", esp)

        # Populate the filesystem without mounting it.
        run("mmd", "-i", esp, "::/EFI")
        run("mmd", "-i", esp, "::/EFI/BOOT")
        run("mmd", "-i", esp, "::/boot")

        run(
            "mcopy",
            "-i", esp,
            args.bootloader.resolve(),
            "::/EFI/BOOT/BOOTX64.EFI",
        )
        run(
            "mcopy",
            "-i", esp,
            args.config.resolve(),
            "::/EFI/BOOT/limine.conf",
        )
        run(
            "mcopy",
            "-i", esp,
            args.kernel.resolve(),
            "::/boot/kernel.elf",
        )

        # Embed the filesystem at the partition's starting sector.
        with disk.open("r+b") as destination, esp.open("rb") as source:
            destination.seek(ESP_START * SECTOR_SIZE)
            shutil.copyfileobj(source, destination)

        # Convert the completed raw disk to modern qcow2.
        run(
            "qemu-img", "convert",
            "-f", "raw",
            "-O", "qcow2",
            "-o", "compat=1.1",
            disk,
            qcow2,
        )

        run("qemu-img", "check", "-f", "qcow2", qcow2)

        # Publish the image only after successful creation and checking.
        qcow2.replace(output)

    print(f"Created {output}")


if __name__ == "__main__":
    main()
