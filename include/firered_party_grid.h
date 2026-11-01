#ifndef GUARD_FIRERED_PARTY_GRID_H
#define GUARD_FIRERED_PARTY_GRID_H

// Row-major 2x3 grid. Directions match the party menu: up=-1, down=1,
// left=-2, right=2. 6 is Confirm; 7 is Cancel. No engine state is modified.
static inline int FireRedPartyGridNext(int slot, int direction, int count, int chooseHalf)
{
    if (count < 1 || count > 6)
        return 7;
    switch (direction)
    {
    case -1:
        if (slot == 7 && chooseHalf)
            return 6;
        if (slot >= 6)
            return count - 1;
        return slot < 2 ? 7 : slot - 2;
    case 1:
        if (slot == 7)
            return 0;
        if (slot == 6)
            return 7;
        return slot + 2 < count ? slot + 2 : (chooseHalf ? 6 : 7);
    case -2:
        return slot < count && (slot & 1) ? slot - 1 : slot;
    case 2:
        return slot < count && !(slot & 1) && slot + 1 < count ? slot + 1 : slot;
    default:
        return slot;
    }
}

#endif
