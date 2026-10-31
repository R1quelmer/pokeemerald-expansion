// Opt-in fixtures for actual emulator screenshots. Not in production builds.
#if defined(FIRERED) && defined(VISUAL_QA)
#include "global.h"
#include "main.h"
#include "new_game.h"
#include "pokemon.h"
#include "party_menu.h"
#include "pokemon_summary_screen.h"
#include "item_menu.h"
#include "item.h"
#include "pokedex.h"
#include "option_menu.h"
#include "trainer_card.h"
#include "naming_screen.h"
#include "pokemon_storage_system.h"
#include "string_util.h"
#include "event_data.h"
#include "battle.h"
#include "constants/items.h"
#include "constants/flags.h"
#include "constants/pokedex.h"

EWRAM_DATA u8 gVisualQaScene = 0;
static bool8 sPrepared;

static void ReturnFromVisualQA(void)
{
    // Stay in the selected scene on a fresh boot; never write a save file.
    SetMainCallback2(CB2_InitOptionMenu);
}

bool8 TryInitFireRedVisualQA(void)
{
    if (sPrepared || gVisualQaScene == 0)
        return FALSE;
    sPrepared = TRUE;
    Sav2_ClearSetDefault();
    NewGameInitData();
    StringCopy(gSaveBlock2Ptr->playerName, _("RED"));
    StringCopy(gSaveBlock1Ptr->rivalName, _("BLUE"));
    const enum Species species[] = {SPECIES_TREECKO, SPECIES_TOTODILE,
        SPECIES_FENNEKIN, SPECIES_SCEPTILE, SPECIES_FERALIGATR, SPECIES_DELPHOX};
    for (u32 i = 0; i < PARTY_SIZE; i++)
    {
        CreateMon(&gPlayerParty[i], species[i], 25 + i * 5, 31, FALSE, 0, OT_ID_PLAYER_ID, 0);
        GetSetPokedexFlag(SpeciesToNationalPokedexNum(species[i]), FLAG_SET_SEEN);
        GetSetPokedexFlag(SpeciesToNationalPokedexNum(species[i]), FLAG_SET_CAUGHT);
    }
    gPlayerPartyCount = PARTY_SIZE;
    AddBagItem(ITEM_POTION, 12);
    AddBagItem(ITEM_POKE_BALL, 20);
    AddBagItem(ITEM_RARE_CANDY, 3);
    AddBagItem(ITEM_MEGA_RING, 1);
    FlagSet(FLAG_SYS_POKEDEX_GET);
    gMain.savedCallback = ReturnFromVisualQA;
    switch (gVisualQaScene)
    {
    case 1: SetMainCallback2(CB2_InitOptionMenu); break;
    case 2: SetMainCallback2(CB2_PartyMenuFromStartMenu); break;
    case 3: ShowPokemonSummaryScreen(SUMMARY_MODE_NORMAL, gPlayerParty, 0, PARTY_SIZE - 1, ReturnFromVisualQA); break;
    case 4: GoToBagMenu(ITEMMENULOCATION_FIELD, POCKET_ITEMS, ReturnFromVisualQA); break;
    case 5: SetMainCallback2(CB2_OpenPokedex); break;
    case 6: ShowPlayerTrainerCard(ReturnFromVisualQA); break;
    case 7: DoNamingScreen(NAMING_SCREEN_PLAYER, gSaveBlock2Ptr->playerName, 0, 0, 0, ReturnFromVisualQA); break;
    case 8: ShowPokemonStorageSystemPC(); break;
    case 9:
        ZeroEnemyPartyMons();
        CreateMon(&gEnemyParty[0], SPECIES_FENNEKIN, 5, 31, FALSE, 0, OT_ID_PLAYER_ID, 0);
        gBattleTypeFlags = BATTLE_TYPE_FIRST_BATTLE;
        SetMainCallback2(CB2_InitBattle);
        break;
    }
    return TRUE;
}
#endif
