kernel_sources = files(
    'src/main.c',
)

kernel_includes = [
    include_directories('include'),
    include_directories('../contrib/limine/include', is_system : true),
]

kernel_linker_script = files('src/arch/x86_64/linker.ld')

kernel = executable(
    'kernel',
    kernel_sources,
    name_suffix : 'elf',
    include_directories : kernel_includes,
    c_args : [
        '-ffreestanding',
        '-fno-stack-protector',
        '-fno-pic',
        '-fno-pie',
        '-fno-omit-frame-pointer',
        '-mno-red-zone',
        '-mgeneral-regs-only',
        '-mcmodel=kernel',
        # Strict ISO C23 plus explicitly documented platform facilities.
        '-pedantic-errors',
        '-Wgnu',
        '-Wconversion',
        '-Wsign-conversion',
        '-Wshadow',
        '-Wcast-qual',
        '-Wcast-align',
        '-Wpointer-arith',
        '-Wwrite-strings',
        '-Wmissing-prototypes',
        '-Wmissing-variable-declarations',
        '-Wstrict-prototypes',
        '-Wswitch-enum',
        '-Wimplicit-fallthrough',
        '-Wvla',
        '-Wundef',
        '-Wformat=2',
        '-Wformat-security',
        '-Wdouble-promotion',
        '-Wnull-dereference',
        '-Wuninitialized',
        '-Waddress-of-packed-member',
    ],
    link_args : [
        '-nostdlib',
        '-static',
        '-Wl,--build-id=none',
        '-Wl,-z,max-page-size=0x1000',
        '-Wl,-T,@0@'.format(kernel_linker_script[0].full_path()),
    ],
    link_depends : kernel_linker_script,
    override_options : [
        'c_std=c23',
        'warning_level=3',
        'werror=true',
        'b_pie=false',
        'b_lto=false',
        'b_sanitize=none',
    ],
    install : false,
)
