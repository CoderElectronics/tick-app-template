/**
 * Author: Ari Stehney
 * VM Application for mirror-os
 */

#include "mirror_target.h"
#include "mirror_bindings.h"

int main(void) {
    stackprotect();

    int x = 64;

    // Main execution loop
    while (true) {
        mixel_draw_pixel(x, 64, 0xF800);
        mixel_draw_line(0, 0, 128, 128, 0x07E0);

        x++;
        yield(0);
    }

    return 0;
}
