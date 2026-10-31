/* Headless mGBA runner. The ROM stays on the runner; only PNGs are exported.
 * Usage: capture ROM output-dir scene-address progress-address main-address flags-address outcome-address
 * Build: cc capture.c -o capture -lmgba
 */
#include <mgba/core/core.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>

int main(int argc, char **argv)
{
    if (argc != 8) return 2;
    unsigned address = strtoul(argv[3], NULL, 16);
    unsigned progressAddress = strtoul(argv[4], NULL, 16);
    unsigned mainAddress = strtoul(argv[5], NULL, 16);
    unsigned flagsAddress = strtoul(argv[6], NULL, 16);
    unsigned outcomeAddress = strtoul(argv[7], NULL, 16);
    for (unsigned scene = 0; scene <= 30; ++scene)
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
        unsigned readyFrame = 0;
        unsigned frameCount = scene == 10 ? 12000 : 2800;
        for (unsigned frame = 0; frame < frameCount; ++frame)
        {
            /* Copyright/intro/title advance with START, then fixture launch.
             * Keep the scenario byte fresh across startup RAM initialization. */
            if (!(core->busRead8(core, address) & 0x80))
            {
                core->busWrite8(core, address, scene);
                core->setKeys(core, frame < 1400 && frame % 90 < 2 ? 8 : 0);
            }
            else
            {
                if (!readyFrame) readyFrame = frame;
                unsigned age = frame - readyFrame;
                unsigned keys = 0;
                if (scene == 10)
                {
                    if (age >= 180 && age < 196) keys = 128; /* DOWN onto real map trigger */
                    if (age >= 240 && age % 45 < 2 && !(age >= 1000 && age < 1300))
                        keys = 1; /* Pause on the complete trainer challenge, then continue. */
                }
                if (scene >= 11 && scene <= 17)
                {
                    if (age == 420 || age == 421) keys = 1; /* open actions */
                    if (age == 480 || age == 481) keys = 2;
                    if (age == 540 || age == 541) keys = 16;
                    if (age == 600 || age == 601 || age == 660 || age == 661) keys = 128;
                    if (age == 720 || age == 721) keys = 32;
                    if (age == 780 || age == 781) keys = 64;
                    if (age == 960 || age == 961) keys = 2; /* cancel to fixture return */
                }
                if (scene == 22 || scene == 23 || scene == 29)
                {
                    if (age == 600 || age == 601) keys = 16;
                    if (scene == 23 && (age == 780 || age == 781)) keys = 16;
                    if (scene == 23 && (age == 1000 || age == 1001)) keys = 1;
                    if (scene == 23 && (age == 1180 || age == 1181)) keys = 128;
                }
                if (scene == 4)
                {
                    if (age == 420 || age == 421 || age == 600 || age == 601
                        || age == 780 || age == 781 || age == 960 || age == 961
                        || age == 1140 || age == 1141) keys = 16;
                    if (age == 1500 || age == 1501) keys = 128;
                    if (age == 1560 || age == 1561) keys = 1;
                    if (age == 1680 || age == 1681 || age == 1800 || age == 1801) keys = 2;
                }
                if (scene == 8)
                {
                    if (age == 600 || age == 601) keys = 16;
                    if (age == 780 || age == 781) keys = 1;
                    if (age == 960 || age == 961) keys = 2;
                }
                if (scene == 26)
                {
                    if (age == 420 || age == 421 || age == 540 || age == 541) keys = 1;
                    if (age == 900 || age == 901 || age == 1100 || age == 1101) keys = 16;
                    if (age == 1500 || age == 1501 || age == 1700 || age == 1701) keys = 2;
                }
                if (scene == 27)
                {
                    if (age == 600 || age == 601 || age == 720 || age == 721) keys = 128;
                    if (age == 840 || age == 841) keys = 1;
                    if (age == 1100 || age == 1101) keys = 16;
                    if (age == 1400 || age == 1401) keys = 2;
                }
                if (scene == 30)
                {
                    if (age == 240 || age == 241) keys = 8;
                    if (age == 420 || age == 421 || age == 540 || age == 541) keys = 128;
                    if (age == 660 || age == 661) keys = 1;
                    if (age == 1200 || age == 1201 || age == 1600 || age == 1601) keys = 2;
                }
                core->setKeys(core, keys);
            }
            core->runFrame(core);
            if (frame == 1800 || frame == 2300 || frame == frameCount - 1
                || (scene == 10 && frame >= 300 && frame % 60 == 0)
                || (scene == 10 && frame >= 1400 && frame <= 2600 && frame % 15 == 0)
                || (scene >= 11 && scene <= 17 && readyFrame && frame - readyFrame >= 360
                    && frame - readyFrame <= 1020 && (frame - readyFrame) % 60 == 30)
                || (scene == 4 && readyFrame && frame - readyFrame >= 360
                    && frame - readyFrame <= 1860 && (frame - readyFrame) % 60 == 30)
                || (scene == 8 && readyFrame && frame - readyFrame >= 360
                    && frame - readyFrame <= 1020 && (frame - readyFrame) % 60 == 30)
                || (scene == 26 && readyFrame && frame - readyFrame >= 360
                    && frame - readyFrame <= 1800 && (frame - readyFrame) % 60 == 30)
                || ((scene == 23 || scene == 27 || scene == 30) && readyFrame && frame - readyFrame >= 360
                    && frame - readyFrame <= 1800 && (frame - readyFrame) % 60 == 30))
            {
                char path[512];
                snprintf(path, sizeof(path), "%s/scene-%02u-frame-%04u.png", argv[2], scene, frame);
                struct VFile *file = VFileOpen(path, O_CREAT | O_TRUNC | O_WRONLY);
                if (!file || !mCoreTakeScreenshotVF(core, file)) return 5;
                file->close(file);
                uint32_t pc = 0;
                core->readRegister(core, "r15", &pc);
                printf("scene=%u frame=%u progress=%u callback2=%08x pc=%08x flags=%08x outcome=%u\n",
                    scene, frame, core->busRead32(core, progressAddress),
                    core->busRead32(core, mainAddress + 4), pc,
                    core->busRead32(core, flagsAddress), core->busRead8(core, outcomeAddress));
            }
        }
        if (scene != 0 && !(core->busRead8(core, address) & 0x80))
        {
            fprintf(stderr, "Visual QA scene %u never reached its menu (progress %u)\n",
                    scene, core->busRead32(core, progressAddress));
            return 6;
        }
        core->deinit(core);
        free(pixels);
    }
    return 0;
}
