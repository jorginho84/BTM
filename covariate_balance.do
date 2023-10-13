/*
* =========================================================
	project: BTM
	date: 01-07-2023
	objective:  generate (Fig 4)
* =========================================================
*/

* ------------------------------------------------------------------------------- *
* ----------------------- GLOBALES: UBICACION DE ARCHIVOS ----------------------- *
* ------------------------------------------------------------------------------- *
	
global entrada "\\nas05\Repositorio_Datos_ADM\07_BASES_INN\02_RIS_INVESTIGACION\RIS_INVESTIGACION_2\01_UANDES_EFECTO_SUBISIDO_CONTRATACION_EMPLEO_FEMENINO\02_DATOS_ENTRADA\12_BTM\Ejercicios"
global dir_graph "R:\04_RESULTADOS\New Graph"
global results "R:\04_RESULTADOS"
global salida "R:\03_DATOS_SALIDA"
global salida2 "C:\Users\ris_schavez\Desktop\SALIDA"
global log_dir "R:\05_RESPALDO_ALGORITMOS\log_file"


* ------------------------------------------------------------------------------- *
* ---------------------------------- PREÁMBULO ---------------------------------- *
* ------------------------------------------------------------------------------- *

clear all

clear matrix
clear mata
set more off
set maxvar 100000

// fijar directorio para ado files
sysdir set PLUS "C:\ado\plus"

// abrir log
cap log close
*log using "$lod_dir\log_employment_main.txt", text replace

* ------------------------------------------------------------------------------- *
* ------------------------------- TRABAJO DE BBDD ------------------------------- *
* ------------------------------------------------------------------------------- *

use "/Users/antoniaaguilera/Desktop/BTM-paper/data/data_sim.dta", clear

// abrir base 
*use  "$salida\rentas_wide_new.dta",clear

// rename PFSE
rename PFSE_*_cent PFSE_cent_*

// crear variable ingreso_anual
egen ingreso_anual = rowmean(rem_2011m6 rem_2011m7 rem_2011m8 rem_2011m9 rem_2011m10 rem_2011m11 rem_2011m12 rem_2012m1 rem_2012m2 rem_2012m3 rem_2012m4 rem_2012m5 rem_2012m6)

cap drop PFSE_prom*
egen min_pf = rowmin(PFSE_cent_*)

// Covariates measured at 2012, before program began
rename (anios_educ_2012m1 n_hijos_2012m1 n_hijos_menores_2012m1 pareja_2012m1) (anios_educ n_hijos n_hijos_menores pareja)
replace pareja = 0 if pareja==.

// List of covs
local covariates1 ingreso_anual anios_educ n_hijos n_hijos_menores pareja

// ancho de banda
scalar h_optimo = 13.3

// covariate balance graphs
xtile qtil = min_pf if min_pf >= - h_optimo & min_pf <=  h_optimo, nq(20)
bys qtil: egen meanind = mean(min_pf)
foreach v in `covariates1'{
	bys qtil: egen mean_`v' = mean(`v')
}

* ------------------------------------------------------------------------------ *
* ---------------------------------- GRAFICOS ---------------------------------- *
* ------------------------------------------------------------------------------ *

/*
Figuras 4 y 5. Éstas están construidas a partir de regresiones lineales (y = a + xb). Tenemos que mostrar líneas desde regresiones polinomio grado 2 (y = a + xb1 +x^2b2). Me parece que se puede hacer con el comando qfit.
*/

* ---------------------------- *
* ---------- LINEAR ---------- *
* ---------------------------- *

// ingreso anual
tw lfitci ingreso_anual min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	lfitci ingreso_anual min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_ingreso_anual meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, /// 
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Anual Earnings") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_ingreso_anual",  replace
graph export "$salida/rdplot_pooled_ingreso_anual.pdf", as(pdf) replace

// años educ
tw lfitci anios_educ min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	lfitci anios_educ min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_anios_educ meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, ///
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Education Years") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_anios_educ",  replace
graph export "$salida/rdplot_pooled_anios_educ.pdf", as(pdf) replace

// numero de hijos
tw lfitci n_hijos min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	lfitci n_hijos min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_n_hijos meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, ///
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Number of Children") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_n_hijos",  replace
graph export "$salida/rdplot_pooled_n_hijos.pdf", as(pdf) replace

// numero de hijos menores
tw lfitci n_hijos_menores min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	lfitci n_hijos_menores min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_n_hijos_menores meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, ///
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Number of minor Children") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_n_hijos_menores",  replace
graph export "$salida/rdplot_pooled_n_hijos_menores.pdf", as(pdf) replace

// pareja
tw lfitci pareja min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	lfitci pareja min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_pareja meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, ///
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Has a Couple") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_pareja",  replace
graph export "$salida/rdplot_pooled_pareja.pdf", as(pdf) replace



* ---------------------------- *
* --------- QUADRATIC -------- *
* ---------------------------- *
scalar h_optimo = 13.3

// ingreso anual 
tw qfitci ingreso_anual min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	qfitci ingreso_anual min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_ingreso_anual meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, /// 
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Anual Earnings") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_ingreso_anual_quad",  replace
graph export "$salida/rdplot_pooled_ingreso_anual_quad.pdf", as(pdf) replace

// años educ
tw qfitci anios_educ min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	qfitci anios_educ min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_anios_educ meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, ///
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Education Years") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_anios_educ_quad",  replace
graph export "$salida/rdplot_pooled_anios_educ_quad.pdf", as(pdf) replace

// numero de hijos
tw qfitci n_hijos min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	qfitci n_hijos min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_n_hijos meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, ///
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Number of Children") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_n_hijos_quad",  replace
graph export "$salida/rdplot_pooled_n_hijos_quad.pdf", as(pdf) replace

// numero de hijos menores
tw qfitci n_hijos_menores min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	qfitci n_hijos_menores min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_n_hijos_menores meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, ///
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Number of minor Children") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_n_hijos_menores_quad",  replace
graph export "$salida/rdplot_pooled_n_hijos_menores_quad.pdf", as(pdf) replace

// pareja
tw qfitci pareja min_pf if min_pf >= - h_optimo & min_pf<=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	qfitci pareja min_pf if min_pf <=  h_optimo & min_pf>=0, ///
	level(95) ciplot(rline) alpattern(dash) lcolor(black) ///
	legend(off) || ///
	scatter mean_pareja meanind if min_pf <=  h_optimo & min_pf >= - h_optimo, ///
	mcolor(black)  graphregion(fcolor(white) color(white)) ///
	ytitle("Has a Couple") xtitle("Vulnerability score") xline(0,lcolor(red) ///
	lpattern(dash)) msymbol(Oh) plotregion(fcolor(white) color(white)) //

graph save "$salida/rdplot_pooled_pareja_quad",  replace
graph export "$salida/rdplot_pooled_pareja_quad.pdf", as(pdf) replace
