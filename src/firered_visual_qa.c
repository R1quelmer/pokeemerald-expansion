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
#include "shop.h"
#include "money.h"
#include "pokedex.h"
#include "option_menu.h"
#include "trainer_card.h"
#include "naming_screen.h"
#include "pokemon_storage_system.h"
#include "string_util.h"
#include "event_data.h"
#include "battle.h"
#include "save.h"
#include "task.h"
#include "oak_speech.h"
#include "overworld.h"
#include "field_screen_effect.h"
#include "event_object_movement.h"
#include "constants/map_groups.h"
#include "constants/vars.h"
#include "constants/items.h"
#include "constants/flags.h"
#include "constants/pokedex.h"
#include "constants/pokemon.h"

EWRAM_DATA u8 gVisualQaScene = 0;
EWRAM_DATA volatile u32 gVisualQaProgress = 0;
static EWRAM_DATA u8 sVisualQaNickname[POKEMON_NAME_LENGTH + 1];
static bool8 sPrepared;
void FireRedVisualQA_OpenStorage(void);
void FireRedVisualQA_OpenStorageItems(void);
void FireRedVisualQA_OpenPartyLayout(u8 layout, MainCallback callback);
void CB2_ReinitMainMenu(void);

static void Task_VisualQaShop(u8 taskId)
{
    static const u16 items[] = {ITEM_POTION, ITEM_SUPER_POTION, ITEM_HYPER_POTION,
        ITEM_POKE_BALL, ITEM_GREAT_BALL, ITEM_ULTRA_BALL, ITEM_FULL_RESTORE,
        ITEM_REVIVE, ITEM_MAX_REPEL, ITEM_ESCAPE_ROPE, ITEM_NONE};
    if (++gTasks[taskId].data[0] == 120)
    {
        CreatePokemartMenu(items);
        DestroyTask(taskId);
    }
}

static void FieldCB_VisualQaShop(void)
{
    FieldCB_WarpExitFadeFromBlack();
    CreateTask(Task_VisualQaShop, 10);
}

static void FieldCB_VisualQaRival(void)
{
    // Resume immediately before the real coordinate trigger at (6,8).
    // Local ID 8 is Blue in PalletTown_ProfessorOaksLab_Frlg/map.json.
    TryMoveObjectEventToMapCoords(8, MAP_NUM(MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB),
        MAP_GROUP(MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB), 10, 5);
    FieldCB_WarpExitFadeFromBlack();
}

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
        GiveMonInitialMoveset(&gParties[B_TRAINER_PLAYER][i]);
        GetSetPokedexFlag(SpeciesToNationalPokedexNum(species[i]), FLAG_SET_SEEN);
        GetSetPokedexFlag(SpeciesToNationalPokedexNum(species[i]), FLAG_SET_CAUGHT);
    }
    gPartiesCount[B_TRAINER_PLAYER] = PARTY_SIZE;
    gVisualQaProgress = 13;
    AddBagItem(ITEM_POTION, 12);
    AddBagItem(ITEM_POKE_BALL, 20);
    AddBagItem(ITEM_RARE_CANDY, 3);
    AddBagItem(ITEM_MEGA_RING, 1);
    AddBagItem(ITEM_ORAN_BERRY, 15);
    AddBagItem(ITEM_TM01, 2);
    FlagSet(FLAG_SYS_POKEDEX_GET);
    if (scene >= 11 && scene <= 16)
    {
        gPartiesCount[B_TRAINER_PLAYER] = scene - 10;
        for (u32 i = scene - 10; i < PARTY_SIZE; i++)
            ZeroMonData(&gParties[B_TRAINER_PLAYER][i]);
    }
    if (scene == 17)
    {
        u16 hp = 0, item = ITEM_ORAN_BERRY;
        u32 status = STATUS1_POISON;
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_HP, &hp);
        SetMonData(&gParties[B_TRAINER_PLAYER][1], MON_DATA_STATUS, &status);
        SetMonData(&gParties[B_TRAINER_PLAYER][2], MON_DATA_HELD_ITEM, &item);
    }
    if (scene == 28)
    {
        bool8 isEgg = TRUE;
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_IS_EGG, &isEgg);
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_NICKNAME, COMPOUND_STRING("EGG"));
    }
    if (scene == 29 || scene == 42)
    {
        u16 item = ITEM_CHARIZARDITE_X;
        u32 status = STATUS1_POISON;
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_STATUS, &status);
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_HELD_ITEM, &item);
    }
    if (scene == 32 || scene == 45 || scene == 46)
    {
        const enum Species edgeSpecies[] = {SPECIES_SHEDINJA, SPECIES_MR_MIME,
            SPECIES_FARFETCHD, SPECIES_WOBBUFFET, SPECIES_FLUTTER_MANE, SPECIES_KINGAMBIT};
        const u8 levels[] = {1, 9, 10, 99, 100, 100};
        for (u32 i = 0; i < PARTY_SIZE; i++)
            CreateMonWithIVs(&gParties[B_TRAINER_PLAYER][i], edgeSpecies[i], levels[i], 0, OTID_STRUCT_PLAYER_ID, 31);
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_NICKNAME, COMPOUND_STRING("WWWWWWWWWWWW"));
        u16 hp = 0, item = ITEM_CHARIZARDITE_X;
        u32 status = STATUS1_PARALYSIS;
        SetMonData(&gParties[B_TRAINER_PLAYER][1], MON_DATA_STATUS, &status);
        SetMonData(&gParties[B_TRAINER_PLAYER][3], MON_DATA_HP, &hp);
        SetMonData(&gParties[B_TRAINER_PLAYER][4], MON_DATA_HELD_ITEM, &item);
        if (scene == 45)
        {
            gPartiesCount[B_TRAINER_PLAYER] = 2;
            for (u32 i = 2; i < PARTY_SIZE; i++)
                ZeroMonData(&gParties[B_TRAINER_PLAYER][i]);
        }
        if (scene == 46)
        {
            hp = 1;
            SetMonData(&gParties[B_TRAINER_PLAYER][5], MON_DATA_HP, &hp);
        }
    }
    if (scene == 33)
    {
        u8 ability = 1;
        CreateMonWithIVs(&gParties[B_TRAINER_PLAYER][0], SPECIES_KINGAMBIT, 100, 0, OTID_STRUCT_PLAYER_ID, 31);
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_ABILITY_NUM, &ability);
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_NICKNAME, COMPOUND_STRING("WWWWWWWWWWWW"));
        SetMonData(&gParties[B_TRAINER_PLAYER][0], MON_DATA_OT_NAME, COMPOUND_STRING("WWWWWWW"));
        SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][0], MOVE_LIGHT_THAT_BURNS_THE_SKY, 0);
        SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][0], MOVE_10_000_000_VOLT_THUNDERBOLT, 1);
        SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][0], MOVE_CLANGOROUS_SOULBLAZE, 2);
        SetMonMoveSlot(&gParties[B_TRAINER_PLAYER][0], MOVE_GUARDIAN_OF_ALOLA, 3);
    }
    if (scene == 35)
        for (u32 item = ITEM_NONE + 1; item < ITEMS_COUNT; item++)
            AddBagItem(item, GetItemPocket(item) == POCKET_KEY_ITEMS ? 1 : 999);
    if (scene == 36)
        ClearBag();
    if (scene == 34 || scene == 42)
    {
        StringCopy(GetBoxNamePtr(0), COMPOUND_STRING("WWWWWWWW"));
        for (u32 i = 0; i < IN_BOX_COUNT; i++)
            SetBoxMonAt(0, i, &gParties[B_TRAINER_PLAYER][i % PARTY_SIZE].box);
    }
    if (scene == 43)
    {
        StringCopy(gSaveBlock2Ptr->playerName, COMPOUND_STRING("WWWWWWW"));
        gSaveBlock2Ptr->playerGender = FEMALE;
        gSaveBlock2Ptr->playTimeHours = 999;
        gSaveBlock2Ptr->playTimeMinutes = 59;
        SetMoney(&gSaveBlock1Ptr->money, MAX_MONEY);
        for (u32 flag = FLAG_BADGE01_GET; flag <= FLAG_BADGE08_GET; flag++)
            FlagSet(flag);
    }
    gVisualQaProgress = 14;
    gMain.savedCallback = ReturnFromVisualQA;
    // The title screen's tasks must not run inside a directly opened menu.
    ResetTasks();
    EnableNationalPokedex();
    gVisualQaScene = scene | 0x80;
    gVisualQaProgress = 20 + scene;
    switch (scene)
    {
    case 1: SetMainCallback2(CB2_InitOptionMenu); break;
    case 2: FireRedVisualQA_OpenPartyLayout(PARTY_LAYOUT_SINGLE, ReturnFromVisualQA); break;
    case 11: case 12: case 13: case 14: case 15: case 16: case 17: case 26: case 32:
        FireRedVisualQA_OpenPartyLayout(PARTY_LAYOUT_SINGLE, ReturnFromVisualQA); break;
    case 24: FireRedVisualQA_OpenPartyLayout(PARTY_LAYOUT_DOUBLE, ReturnFromVisualQA); break;
    case 45: FireRedVisualQA_OpenPartyLayout(PARTY_LAYOUT_DOUBLE, ReturnFromVisualQA); break;
    case 25: FireRedVisualQA_OpenPartyLayout(PARTY_LAYOUT_MULTI_FULL, ReturnFromVisualQA); break;
    case 46: FireRedVisualQA_OpenPartyLayout(PARTY_LAYOUT_MULTI_FULL, ReturnFromVisualQA); break;
    case 3: ShowPokemonSummaryScreen(SUMMARY_MODE_NORMAL, gParties[B_TRAINER_PLAYER], 0, PARTY_SIZE - 1, ReturnFromVisualQA); break;
    case 4: case 35: case 36:
        GoToBagMenu(ITEMMENULOCATION_FIELD, POCKET_ITEMS, ReturnFromVisualQA); break;
    case 18: case 19: case 20: case 21:
        GoToBagMenu(ITEMMENULOCATION_FIELD, scene - 17, ReturnFromVisualQA); break;
    case 22: case 23: case 28: case 29: case 33:
        ShowPokemonSummaryScreen(SUMMARY_MODE_NORMAL, gParties[B_TRAINER_PLAYER], 0, PARTY_SIZE - 1, ReturnFromVisualQA); break;
    case 27: SetMainCallback2(CB2_ReinitMainMenu); break;
    case 31: StartNewGameSceneFrlg(); break;
    case 37:
        VarSet(VAR_MAP_SCENE_VIRIDIAN_CITY_MART, 1);
        SetWarpDestination(MAP_GROUP(MAP_VIRIDIAN_CITY_MART),
            MAP_NUM(MAP_VIRIDIAN_CITY_MART), WARP_ID_NONE, 3, 5);
        WarpIntoMap();
        gFieldCallback = FieldCB_VisualQaShop;
        SetMainCallback2(CB2_LoadMap);
        break;
    case 30:
        FlagSet(FLAG_SYS_POKEMON_GET);
        SetWarpDestination(MAP_GROUP(MAP_PALLET_TOWN_PLAYERS_HOUSE_2F),
            MAP_NUM(MAP_PALLET_TOWN_PLAYERS_HOUSE_2F), WARP_ID_NONE, 6, 6);
        WarpIntoMap();
        gFieldCallback = FieldCB_WarpExitFadeFromBlack;
        SetMainCallback2(CB2_LoadMap);
        break;
    case 5: case 39: case 40: SetMainCallback2(CB2_OpenPokedex); break;
    case 6: case 43: ShowPlayerTrainerCard(ReturnFromVisualQA); break;
    case 7: DoNamingScreen(NAMING_SCREEN_PLAYER, gSaveBlock2Ptr->playerName, 0, 0, 0, ReturnFromVisualQA); break;
    case 38:
        StringCopy(sVisualQaNickname, COMPOUND_STRING("WWWWWWWWWWWW"));
        DoNamingScreen(NAMING_SCREEN_NICKNAME, sVisualQaNickname,
            SPECIES_TREECKO, MON_MALE, 0, ReturnFromVisualQA); break;
    case 44:
        StringCopy(sVisualQaNickname, COMPOUND_STRING("WWWWWWWW"));
        DoNamingScreen(NAMING_SCREEN_BOX, sVisualQaNickname, 0, 0, 0, ReturnFromVisualQA); break;
    case 34: FireRedVisualQA_OpenStorage(); break;
    case 42: FireRedVisualQA_OpenStorageItems(); break;
    case 8:
        for (u32 i = 0; i < PARTY_SIZE; i++)
            SetBoxMonAt(0, i, &gParties[B_TRAINER_PLAYER][i].box);
        FireRedVisualQA_OpenStorage(); break;
    case 9: case 41:
        ZeroEnemyPartyMons();
        CreateMonWithIVs(&gParties[B_TRAINER_OPPONENT_A][0], SPECIES_FENNEKIN, 5, 0, OTID_STRUCT_PLAYER_ID, 31);
        GiveMonInitialMoveset(&gParties[B_TRAINER_OPPONENT_A][0]);
        gBattleTypeFlags = scene == 9 ? BATTLE_TYPE_FIRST_BATTLE : 0;
        SetMainCallback2(CB2_InitBattle);
        break;
    case 10:
        ZeroPlayerPartyMons();
        CreateMonWithIVs(&gParties[B_TRAINER_PLAYER][0], SPECIES_TREECKO, 5, 0, OTID_STRUCT_PLAYER_ID, 31);
        GiveMonInitialMoveset(&gParties[B_TRAINER_PLAYER][0]);
        gPartiesCount[B_TRAINER_PLAYER] = 1;
        VarSet(VAR_STARTER_MON, 0);
        VarSet(VAR_MAP_SCENE_PALLET_TOWN_PROFESSOR_OAKS_LAB, 3);
        FlagClear(FLAG_HIDE_OAK_IN_HIS_LAB);
        FlagClear(FLAG_HIDE_RIVAL_IN_LAB);
        SetWarpDestination(MAP_GROUP(MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB),
            MAP_NUM(MAP_PALLET_TOWN_PROFESSOR_OAKS_LAB), WARP_ID_NONE, 6, 7);
        WarpIntoMap();
        gFieldCallback = FieldCB_VisualQaRival;
        SetMainCallback2(CB2_LoadMap);
        break;
    }
    return TRUE;
}
#endif
