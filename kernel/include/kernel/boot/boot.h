#pragma once

#include <limine/limine.h>
#include <stdint.h>

[[gnu::used, gnu::section(".limine_requests_start")]] static volatile uint64_t
  g_limine_requests_start[] = LIMINE_REQUESTS_START_MARKER;

[[gnu::used, gnu::section(".limine_requests")]] static volatile uint64_t
  g_limine_base_revision[] = LIMINE_BASE_REVISION(6);

[[gnu::used, gnu::section(".limine_requests_end")]] static volatile uint64_t
  g_limine_requests_end[] = LIMINE_REQUESTS_END_MARKER;
