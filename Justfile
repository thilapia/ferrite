set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

build_dir := "out"
cross_file := "build/cross/x86_64.ini"

# List available commands.
default:
    @just --list

# Configure a new build or update an existing one.
setup:
    meson setup --reconfigure --cross-file "{{cross_file}}" "{{build_dir}}"

# Build the kernel and disk image.
build:
    meson compile -C "{{build_dir}}"

# Build only the kernel.
kernel:
    meson compile -C "{{build_dir}}" kernel.elf

# Build the bootable qcow2 image.
image:
    meson compile -C "{{build_dir}}" disk-image

# Build and boot normally.
run:
    meson compile -C "{{build_dir}}" run

# Build and start QEMU paused, ready for CLion or LLDB.
debug:
    meson compile -C "{{build_dir}}" debug

# Connect terminal LLDB to an already-running debug instance.
lldb:
    lldb "{{build_dir}}/kernel/kernel.elf" \
        -o "gdb-remote 127.0.0.1:1234" \
        -o "breakpoint set --hardware --name kmain"

# Inspect the generated disk image.
image-info:
    qemu-img info "{{build_dir}}/ferrite.qcow2"

# Remove build outputs through Ninja; preserve firmware settings.
clean:
    meson compile -C "{{build_dir}}" --clean

# Format project-owned C sources and headers, including new files.
format:
    find kernel -type f \( -name '*.c' -o -name '*.h' \) -print0 | xargs -0 -r clang-format --style=file -i

# Check formatting without modifying files.
format-check:
    find kernel -type f \( -name '*.c' -o -name '*.h' \) -print0 | xargs -0 -r clang-format --style=file --dry-run --Werror

# Check project translation units and their included project headers.
tidy: setup
    run-clang-tidy -quiet -p "{{build_dir}}" '(^|/)kernel/.*\.c$'

# Run all local formatting and static-analysis checks.
check: format-check tidy
