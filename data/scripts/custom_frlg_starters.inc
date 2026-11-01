@ Custom FireRed starter choices.
@ Keep the original Kanto starter slot IDs so the existing rival battle routing
@ continues to select the type-advantage branch.

PalletTown_ProfessorOaksLab_EventScript_TreeckoBall::
	lock
	faceplayer
	setvar VAR_TEMP_1, 0
	setvar VAR_TEMP_2, SPECIES_TREECKO
	setvar VAR_TEMP_3, SPECIES_FENNEKIN
	setvar VAR_TEMP_4, 1
	goto PalletTown_ProfessorOaksLab_EventScript_ConfirmCustomStarterChoice
	end

PalletTown_ProfessorOaksLab_EventScript_TotodileBall::
	lock
	faceplayer
	setvar VAR_TEMP_1, 1
	setvar VAR_TEMP_2, SPECIES_TOTODILE
	setvar VAR_TEMP_3, SPECIES_TREECKO
	setvar VAR_TEMP_4, 0
	goto PalletTown_ProfessorOaksLab_EventScript_ConfirmCustomStarterChoice
	end

PalletTown_ProfessorOaksLab_EventScript_FennekinBall::
	lock
	faceplayer
	setvar VAR_TEMP_1, 2
	setvar VAR_TEMP_2, SPECIES_FENNEKIN
	setvar VAR_TEMP_3, SPECIES_TOTODILE
	setvar VAR_TEMP_4, 2
	goto PalletTown_ProfessorOaksLab_EventScript_ConfirmCustomStarterChoice
	end

PalletTown_ProfessorOaksLab_EventScript_ConfirmCustomStarterChoice::
	applymovement LOCALID_OAKS_LAB_PROF_OAK, Common_Movement_FaceRight
	waitmovement 0
	showmonpic VAR_TEMP_2, 10, 3
	textcolor NPC_TEXT_COLOR_MALE
	goto_if_eq VAR_TEMP_1, 0, PalletTown_ProfessorOaksLab_EventScript_ConfirmTreecko
	goto_if_eq VAR_TEMP_1, 1, PalletTown_ProfessorOaksLab_EventScript_ConfirmTotodile
	goto_if_eq VAR_TEMP_1, 2, PalletTown_ProfessorOaksLab_EventScript_ConfirmFennekin
	end

PalletTown_ProfessorOaksLab_EventScript_ConfirmTreecko::
	msgbox PalletTown_ProfessorOaksLab_Text_OakChoosingTreecko, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, PalletTown_ProfessorOaksLab_EventScript_ChoseStarter
	goto_if_eq VAR_RESULT, NO, PalletTown_ProfessorOaksLab_EventScript_DeclinedStarter
	end

PalletTown_ProfessorOaksLab_EventScript_ConfirmTotodile::
	msgbox PalletTown_ProfessorOaksLab_Text_OakChoosingTotodile, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, PalletTown_ProfessorOaksLab_EventScript_ChoseStarter
	goto_if_eq VAR_RESULT, NO, PalletTown_ProfessorOaksLab_EventScript_DeclinedStarter
	end

PalletTown_ProfessorOaksLab_EventScript_ConfirmFennekin::
	msgbox PalletTown_ProfessorOaksLab_Text_OakChoosingFennekin, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, PalletTown_ProfessorOaksLab_EventScript_ChoseStarter
	goto_if_eq VAR_RESULT, NO, PalletTown_ProfessorOaksLab_EventScript_DeclinedStarter
	end

PalletTown_ProfessorOaksLab_Text_OakChoosingTreecko::
	.string "I see! TREECKO is your choice.\n"
	.string "It's very easy to raise.\p"
	.string "So, {PLAYER}, you want to go with\n"
	.string "the GRASS POKéMON TREECKO?$"

PalletTown_ProfessorOaksLab_Text_OakChoosingTotodile::
	.string "Hm! TOTODILE is your choice.\n"
	.string "It's one worth raising.\p"
	.string "So, {PLAYER}, you've decided on the\n"
	.string "WATER POKéMON TOTODILE?$"

PalletTown_ProfessorOaksLab_Text_OakChoosingFennekin::
	.string "Ah! FENNEKIN is your choice.\n"
	.string "You should raise it patiently.\p"
	.string "So, {PLAYER}, you're claiming the\n"
	.string "FIRE POKéMON FENNEKIN?$"
