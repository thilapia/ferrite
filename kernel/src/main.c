#include <stdint.h>
#include <limine/limine.h>

__attribute__((used, section(".limine_requests_start")))
static volatile uint64_t limine_requests_start[] = LIMINE_REQUESTS_START_MARKER;

__attribute__((used, section(".limine_requests")))
static volatile uint64_t limine_base_revision[] = LIMINE_BASE_REVISION(6);

__attribute__((used, section(".limine_requests_end")))
static volatile uint64_t limine_requests_end[] = LIMINE_REQUESTS_END_MARKER;

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
