project(
    'ferrite',
    'c',
    version : '0.1.0',
    meson_version : '>=1.12.1',
    default_options : [
        'c_std=c23',
        'warning_level=3',
        'buildtype=debug',
    ],
)

if not meson.is_cross_build()
    error('Configure the project with \'--cross-file build/cross/x86_64.ini\'')
endif

if host_machine.cpu_family() != 'x86_64'
    error('Only x86_64 is currently supported')
endif

# Kernel target configuration
subdir('kernel')

uv = find_program('uv', native : true)

image_script = files('build/scripts/make-image.py')
limine_bootloader = files('contrib/limine/BOOTX64.EFI')

limine_config = configure_file(
    input : 'build/limine.conf.in',
    output : 'limine.conf',
    copy : true,
)

disk_image = custom_target(
    'disk-image',
    input : [
        kernel,
        limine_bootloader,
        limine_config,
    ],
    output : 'ferrite.qcow2',
    command : [
        uv, 'run', '--script', image_script,
        '--kernel', '@INPUT0@',
        '--bootloader', '@INPUT1@',
        '--config', '@INPUT2@',
        '--output', '@OUTPUT@',
    ],
    depend_files : image_script,
    build_by_default : true,
)

qemu_script = files('build/scripts/run-qemu.py')

run_target(
    'run',
    command : [
        uv, 'run', '--script', qemu_script,
        '--image', disk_image,
    ],
    depends : disk_image,
)

run_target(
    'debug',
    command : [
        uv, 'run', '--script', qemu_script,
        '--image', disk_image,
        '--debug',
    ],
    depends : disk_image,
)