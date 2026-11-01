#include <assert.h>
#include "../../include/firered_party_grid.h"

int main(void)
{
    // Every reachable slot and exit must stay valid for partial parties.
    const int directions[] = {-1, 1, -2, 2};
    for (int count = 1; count <= 6; count++)
        for (int half = 0; half <= 1; half++)
            for (int slot = 0; slot <= 7; slot++)
            {
                if (slot >= count && slot < 6) continue;
                if (slot == 6 && !half) continue;
                for (int d = 0; d < 4; d++)
                {
                    int next = FireRedPartyGridNext(slot, directions[d], count, half);
                    assert((next >= 0 && next < count) || next == 7 || (half && next == 6));
                }
            }
    assert(FireRedPartyGridNext(0, 2, 6, 0) == 1);
    assert(FireRedPartyGridNext(1, 1, 6, 0) == 3);
    assert(FireRedPartyGridNext(3, 1, 6, 0) == 5);
    assert(FireRedPartyGridNext(5, -2, 6, 0) == 4);
    assert(FireRedPartyGridNext(4, -1, 6, 0) == 2);
    assert(FireRedPartyGridNext(2, -1, 6, 0) == 0);
    assert(FireRedPartyGridNext(4, 2, 5, 0) == 4);
    assert(FireRedPartyGridNext(4, 1, 5, 0) == 7);
    assert(FireRedPartyGridNext(7, -1, 5, 1) == 6);
    assert(FireRedPartyGridNext(6, -1, 5, 1) == 4);
    assert(FireRedPartyGridNext(0, 1, 1, 0) == 7);
    assert(FireRedPartyGridNext(7, 1, 1, 0) == 0);
    return 0;
}
