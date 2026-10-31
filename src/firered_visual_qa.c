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
#include "save.h"
#include "constants/items.h"
#include "constants/flags.h"
#include "constants/pokedex.h"

EWRAM_DATA u8 gVisualQaScene = 0;
EWRAM_DATA volatile u32 gVisualQaProgress = 0;
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
    u8 scene = gVisualQaScene;
    gVisualQaProgress = 10;
    SetVBlankCallback(NULL);
    SetHBlankCallback(NULL);
    Sav2_ClearSetDefault();
    gVisualQaProgress = 11;
    // These fixtures exercise menus, not RTC provisioning. An isolated
    // headless cartridge has no user's persisted RTC/save handshake.
    gSaveFileStatus = SAVE_STATUS_OK;
    // NewGameInitData preserves the rival name on the stack. A zeroed save
    // is not an EOS-terminated game string; seed it before that copy.
    StringCopy(gSaveBlock1Ptr->rivalName, COMPOUND_STRING("BLUE"));
    NewGameInitData();
    gVisualQaProgress = 12;
    StringCopy(gSaveBlock2Ptr->playerName, COMPOUND_STRING("RED"));
    StringCopy(gSaveBlock1Ptr->rivalName, COMPOUND_STRING("BLUE"));
    const enum Species species[] = {SPECIES_TREECKO, SPECIES_TOTODILE,
        SPECIES_FENNEKIN, SPECIES_SCEPTILE, SPECIES_FERALIGATR, SPECIES_DELPHOX};
    for (u32 i = 0; i < PARTY_SIZE; i++)
    {
        CreateMonWithIVs(&gParties[B_TRAINER_PLAYER][i], species[i], 25 + i * 5, 0, OTID_STRUCT_PLAYER_ID, 31);
        GetSetPokedexFlag(SpeciesToNationalPokedexNum(species[i]), FLAG_SET_SEEN);
        GetSetPokedexFlag(SpeciesToNationalPokedexNum(species[i]), FLAG_SET_CAUGHT);
    }
    gPartiesCount[B_TRAINER_PLAYER] = PARTY_SIZE;
    gVisualQaProgress = 13;
    AddBagItem(ITEM_POTION, 12);
    AddBagItem(ITEM_POKE_BALL, 20);
    AddBagItem(ITEM_RARE_CANDY, 3);
    AddBagItem(ITEM_MEGA_RING, 1);
    FlagSet(FLAG_SYS_POKEDEX_GET);
    gVisualQaProgress = 14;
    gMain.savedCallback = ReturnFromVisualQA;
    gVisualQaScene = scene | 0x80;
    gVisualQaProgress = 20 + scene;
    switch (scene)
    {
    case 1: SetMainCallback2(CB2_InitOptionMenu); break;
    case 2: SetMainCallback2(CB2_PartyMenuFromStartMenu); break;
    case 3: ShowPokemonSummaryScreen(SUMMARY_MODE_NORMAL, gParties[B_TRAINER_PLAYER], 0, PARTY_SIZE - 1, ReturnFromVisualQA); break;
    case 4: GoToBagMenu(ITEMMENULOCATION_FIELD, POCKET_ITEMS, ReturnFromVisualQA); break;
    case 5: SetMainCallback2(CB2_OpenPokedex); break;
    case 6: ShowPlayerTrainerCard(ReturnFromVisualQA); break;
    case 7: DoNamingScreen(NAMING_SCREEN_PLAYER, gSaveBlock2Ptr->playerName, 0, 0, 0, ReturnFromVisualQA); break;
    case 8: ShowPokemonStorageSystemPC(); break;
    case 9:
        ZeroEnemyPartyMons();
        CreateMonWithIVs(&gParties[B_TRAINER_OPPONENT_A][0], SPECIES_FENNEKIN, 5, 0, OTID_STRUCT_PLAYER_ID, 31);
        gBattleTypeFlags = BATTLE_TYPE_FIRST_BATTLE;
        SetMainCallback2(CB2_InitBattle);
        break;
    }
    return TRUE;
}
#endif
