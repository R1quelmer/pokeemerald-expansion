#ifdef FIRERED
#include "global.h"
#include "firered_ui.h"
#include "menu.h"
#include "string_util.h"
#include "text.h"
#include "window.h"

static bool32 WrapParagraph(u8 *dst, const u8 *src, u32 font, u32 width, u32 height, u32 lineHeight)
{
    u32 length = 0, lineStart = 0, lines = 1;
    s32 space = -1;
    while (length < 511 && src[length] != EOS)
    {
        dst[length] = src[length];
        length++;
    }
    dst[length] = EOS;
    for (u32 pos = 0; pos < length;)
    {
        u32 next = pos + 1;
        if (dst[pos] == CHAR_NEWLINE)
        {
            lines++;
            lineStart = next;
            space = -1;
            pos = next;
            continue;
        }
        if (dst[pos] == EXT_CTRL_CODE_BEGIN)
            next += GetExtCtrlCodeLength(dst[next]);
        else if (dst[pos] == CHAR_SPACE)
            space = pos;
        u8 saved = dst[next];
        dst[next] = EOS;
        s32 pixels = GetStringWidth(font, dst + lineStart, 0);
        dst[next] = saved;
        if (pixels > width)
        {
            if (space < (s32)lineStart)
                return FALSE;
            dst[space] = CHAR_NEWLINE;
            lineStart = space + 1;
            space = -1;
            lines++;
        }
        pos = next;
    }
    return lines * lineHeight <= height;
}

void FireRedPrintParagraph(u8 windowId, const u8 *text, u8 x, u8 y, const u8 colors[3])
{
    u8 wrapped[512];
    const u8 fonts[] = {FONT_SMALL, FONT_SMALL_NARROW, FONT_SMALL_NARROWER};
    // Narrow fonts report an 8px advance, while their glyphs occupy 12/15px.
    // Use actual occupied heights for wrapping and provide the missing spacing.
    const u8 heights[] = {13, 12, 16};
    u32 font = fonts[0];
    u32 lineHeight = heights[0];
    u32 width = WindowWidthPx(windowId) - x;
    u32 height = GetWindowAttribute(windowId, WINDOW_HEIGHT) * 8 - y;
    for (u32 i = 0; i < ARRAY_COUNT(fonts); i++)
    {
        font = fonts[i];
        lineHeight = heights[i];
        if (WrapParagraph(wrapped, text, font, width, height, lineHeight))
            break;
    }
    AddTextPrinterParameterized4(windowId, font, x, y, 0,
        lineHeight - GetFontAttribute(font, FONTATTR_MAX_LETTER_HEIGHT), colors, 0, wrapped);
}
#endif
