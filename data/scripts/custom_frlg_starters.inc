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
	goto PalletTown_ProfessorOaksLab_EventScript_ConfirmStarterChoice
	end

PalletTown_ProfessorOaksLab_EventScript_TotodileBall::
	lock
	faceplayer
	setvar VAR_TEMP_1, 1
	setvar VAR_TEMP_2, SPECIES_TOTODILE
	setvar VAR_TEMP_3, SPECIES_TREECKO
	setvar VAR_TEMP_4, 0
	goto PalletTown_ProfessorOaksLab_EventScript_ConfirmStarterChoice
	end

PalletTown_ProfessorOaksLab_EventScript_FennekinBall::
	lock
	faceplayer
	setvar VAR_TEMP_1, 2
	setvar VAR_TEMP_2, SPECIES_FENNEKIN
	setvar VAR_TEMP_3, SPECIES_TOTODILE
	setvar VAR_TEMP_4, 2
	goto PalletTown_ProfessorOaksLab_EventScript_ConfirmStarterChoice
	end
