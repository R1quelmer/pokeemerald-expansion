/* Headless mGBA runner. The ROM stays on the runner; only PNGs are exported.
 * Usage: capture ROM output-dir scenario-byte-address progress-address main-address
 * Build: cc capture.c -o capture -lmgba
 */
#include <mgba/core/core.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>

int main(int argc, char **argv)
{
    if (argc != 6) return 2;
    unsigned address = strtoul(argv[3], NULL, 16);
    unsigned progressAddress = strtoul(argv[4], NULL, 16);
    unsigned mainAddress = strtoul(argv[5], NULL, 16);
    for (unsigned scene = 0; scene <= 9; ++scene)
    {
        struct mCore *core = mCoreFind(argv[1]);
        if (!core || !core->init(core)) return 3;
        mCoreInitConfig(core, NULL);
        mCoreConfigSetDefaultIntValue(&core->config, "skipBios", 1);
        core->loadConfig(core, &core->config);
        color_t *pixels = calloc(256 * 256, sizeof(color_t));
        if (!pixels || !mCoreLoadFile(core, argv[1])) return 4;
        core->setVideoBuffer(core, pixels, 256);
        core->reset(core);
        for (unsigned frame = 0; frame < 2800; ++frame)
        {
            /* Copyright/intro/title advance with START, then fixture launch.
             * Keep the scenario byte fresh across startup RAM initialization. */
            if (!(core->busRead8(core, address) & 0x80))
            {
                core->busWrite8(core, address, scene);
                core->setKeys(core, frame < 1400 && frame % 90 < 2 ? 8 : 0);
            }
            else
                core->setKeys(core, 0);
            core->runFrame(core);
            if (frame == 1800 || frame == 2300 || frame == 2799)
            {
                char path[512];
                snprintf(path, sizeof(path), "%s/scene-%02u-frame-%04u.png", argv[2], scene, frame);
                struct VFile *file = VFileOpen(path, O_CREAT | O_TRUNC | O_WRONLY);
                if (!file || !mCoreTakeScreenshotVF(core, file)) return 5;
                file->close(file);
                uint32_t pc = 0;
                core->readRegister(core, "r15", &pc);
                printf("scene=%u frame=%u progress=%u callback2=%08x pc=%08x\n",
                    scene, frame, core->busRead32(core, progressAddress),
                    core->busRead32(core, mainAddress + 4), pc);
            }
        }
        core->deinit(core);
        free(pixels);
    }
    return 0;
}
