cmake_minimum_required(VERSION 3.20)

# export clangd compile commands so that proper bindings header is picked up
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# cross toolchain selection (mirrors common/makefile.template)
if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Darwin")
    set(TOOLCHAIN_PREFIX "riscv64-elf-")
else()
    set(TOOLCHAIN_PREFIX "riscv64-unknown-elf-")
endif()

find_program(RISCV_GCC ${TOOLCHAIN_PREFIX}gcc)
if(NOT RISCV_GCC)
    if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Darwin")
        message(FATAL_ERROR "${TOOLCHAIN_PREFIX}gcc not found. Try: brew install riscv64-elf-gcc riscv64-elf-binutils")
    else()
        message(FATAL_ERROR "${TOOLCHAIN_PREFIX}gcc not found. Try: apt-get install gcc-riscv64-unknown-elf")
    endif()
endif()

set(CMAKE_C_COMPILER ${RISCV_GCC})
set(CMAKE_ASM_COMPILER ${RISCV_GCC})
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR riscv32)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

project(app C ASM)

find_program(CMAKE_OBJCOPY ${TOOLCHAIN_PREFIX}objcopy)
find_program(CMAKE_OBJDUMP ${TOOLCHAIN_PREFIX}objdump)

set(OPT "-Os" CACHE STRING "Optimization level")

set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/common/linker.ld)
set(TICK_HEADERS_DIR ${CMAKE_SOURCE_DIR}/tick-headers/lib)

# tick-headers is a git submodule; if it hasn't been checked out, fail fast
# with an actionable message instead of a confusing "header not found" error.
if(NOT EXISTS ${TICK_HEADERS_DIR}/mirror_target.h)
    message(FATAL_ERROR
        "tick-headers submodule appears to be missing/empty at "
        "${TICK_HEADERS_DIR}. Run: git submodule update --init --recursive"
    )
endif()

add_executable(app_elf
    src/main.c
    common/crt0.S
)

set_target_properties(app_elf PROPERTIES
    OUTPUT_NAME "app"
    SUFFIX ".elf"
    LINK_DEPENDS ${LINKER_SCRIPT}
)

target_include_directories(app_elf PRIVATE
    ${CMAKE_SOURCE_DIR}/common
    ${TICK_HEADERS_DIR}
)

target_compile_definitions(app_elf PRIVATE MIRROR_APP=1)

target_compile_options(app_elf PRIVATE
    ${OPT}
    -fno-stack-protector
    -fno-builtin-memcpy
    -fno-builtin
    -static-libgcc
    -fdata-sections
    -ffunction-sections
    -g
    -march=rv32im
    -mabi=ilp32
    -static
)

target_link_options(app_elf PRIVATE
    -T${LINKER_SCRIPT}
    -nostdlib
    -Wl,--gc-sections
    -march=rv32im
    -mabi=ilp32
    -static
)

# needed for softfp
target_link_libraries(app_elf PRIVATE gcc)

# Produce a raw binary alongside the ELF, like `objcopy -O binary`
add_custom_command(TARGET app_elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} $<TARGET_FILE:app_elf> -O binary $<TARGET_FILE_DIR:app_elf>/app.bin
    COMMENT "Generating app.bin"
)

# `cmake --build . --target disasm` replaces `make disasm_template`
add_custom_target(disasm
    COMMAND ${CMAKE_OBJDUMP} -S -d -f $<TARGET_FILE:app_elf>
    DEPENDS app_elf
    VERBATIM
)
