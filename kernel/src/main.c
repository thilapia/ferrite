#include <kernel/boot/boot.h>

#include <limine/limine.h>

static _Noreturn void halt(void) {
    for (;;) {
        __asm__ volatile ("cli; hlt" ::: "memory");
    }
}

_Noreturn void kmain(void) {
    if (!LIMINE_BASE_REVISION_SUPPORTED(limine_base_revision)) {
        halt();
    }

    // Boot protocol accepted. Kernel initialization happens below.

    halt();
}
