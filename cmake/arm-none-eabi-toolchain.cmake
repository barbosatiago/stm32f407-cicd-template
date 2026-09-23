set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

find_program(
    ARM_GCC
    arm-none-eabi-gcc
    REQUIRED
)

find_program(
    ARM_OBJCOPY
    arm-none-eabi-objcopy
    REQUIRED
)

find_program(
    ARM_SIZE
    arm-none-eabi-size
    REQUIRED
)

find_program(
    ARM_OBJDUMP
    arm-none-eabi-objdump
    REQUIRED
)

set(CMAKE_C_COMPILER "${ARM_GCC}")
set(CMAKE_ASM_COMPILER "${ARM_GCC}")

set(CMAKE_OBJCOPY "${ARM_OBJCOPY}")
set(CMAKE_SIZE "${ARM_SIZE}")
set(CMAKE_OBJDUMP "${ARM_OBJDUMP}")

set(CMAKE_EXECUTABLE_SUFFIX ".elf")