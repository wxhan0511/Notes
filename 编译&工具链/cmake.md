
# 通用模板

set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/STM32F407VGTX_FLASH.ld)
add_compile_options(-mcpu=cortex-m4 -mthumb -mthumb-interwork)
add_link_options(-mcpu=cortex-m3 -mthumb -mthumb-interwork)
add_definitions(-DDEBUG -DUSE_HAL_DRIVER -DSTM32F407xx)
