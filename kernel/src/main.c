#include <kernel/boot/boot.h>
#include <kernel/entry.h>

#include <limine/limine.h>

[[noreturn]] static void halt() {
  for (;;) {
    __asm__ volatile("cli; hlt" ::: "memory");
  }
}

[[noreturn]] void kmain() {
  if (!LIMINE_BASE_REVISION_SUPPORTED(g_limine_base_revision)) {
    halt();
  }

  // Boot protocol accepted. Kernel initialization happens below.

  halt();
}
