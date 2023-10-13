/*
* =========================================================
	project: BTM
	date: 10-08-2023
	objective: This do-file estimates static treatment 
	effects, employment and earnings (Fig 5)
	Table 3
	running var: d_eleg_ever (min_pf)
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

global salida "/Users/antoniaaguilera/Desktop/BTM-paper/"
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

/*
Para ello, primero hay que usar el comando "rdwinselect" (usar como covariates las que aparecen en tabla de estadística descriptiva) para escoger la ventana óptima. Esta ventana se debe usar en el comando "rdrandinf", que estima los efectos
*/

* ------------------------------------------------------------------------------- *
* ------------------------------- TRABAJO DE BBDD ------------------------------- *
* ------------------------------------------------------------------------------- *

// abrir base 
*use  "$salida\rentas_wide_new.dta",clear
* --- borrar esto
use "/Users/antoniaaguilera/Desktop/BTM-paper/data/data_sim.dta", clear
* --- borrar esto

drop rem_2011m* 

// create monthly employment
forvalues y = 2012/2015 {
	if `y' == 2012 {
		forvalues m = 7/12 {
				gen emp_`y'm`m' = .
				replace emp_`y'm`m' = 0 if rem_`y'm`m' == 0 | rem_`y'm`m' == .
				replace emp_`y'm`m' = 1 if rem_`y'm`m' != 0 & rem_`y'm`m' != .
		}
	}
	
	else {
		forvalues m = 1/12{
			gen emp_`y'm`m' = .
			replace emp_`y'm`m' = 0 if rem_`y'm`m' == 0 | rem_`y'm`m' == .
			replace emp_`y'm`m' = 1 if rem_`y'm`m' != 0 & rem_`y'm`m' != .
		}
	}
}

// number of months employed
egen n_emp = rowtotal(emp_*)

// log earnings
forvalues y = 2012/2015{
	if `y' == 2012 {
		forvalues m = 7/12{
				gen lw_`y'm`m' = log(rem_`y'm`m')
		}
	}

	else{
		forvalues m = 1/12{
			gen lw_`y'm`m' = log(rem_`y'm`m')
		}
	}
}

egen lw_2 = rowmean(lw_*)

* ------------------------ *
* ------ WIN SELECT ------ *
* ------------------------ *
rdwinselect PFSE_2012m12_cent anios_educ_2012m12 lw_2012m12 n_hijos_2012m12 n_hijos_less18_2012m12 pareja_2012m12, wmin(.5) wstep(.125) reps(10000) //ocupar parámetros por default
 
scalar leftw  = `r(w_left)'
scalar rightw = `r(w_right)'

/*
Dudas: 
- las covariables de qué mes? resumen de las de 2012 ? -> baseline
- parámetros para el winselect? 
- el h_optimo hay que observarlo ahí?
*/

* ------------------------------------------------- *
* -------------- LOCAL RAND APPROACH -------------- *
* ------------------------------------------------- *
// Using best application to estimate effects of eligibility 

forvalues y = 2012/2015{
	forvalues m = 1/12{
		rename PFSE_`y'm`m'_cent PFSE_cent_`y'm`m'	
	}
}

egen min_pf = rowmin(PFSE_cent_*)
gen d_eleg_ever = min_pf<= 0

* ---------------------------------------- *
* --------- HETEROGENEOUS EFFECTS -------- *
* ---------------------------------------- *
// conservar el valor del mes y año donde el PFSE es el más bajo (el que gatilla elegibilidad)
gen min_month = . 
gen min_year = .

forval year = 2012/2015 {
	forval month = 12(-1)1 {
		replace min_month  = `month'   if min_pf == PFSE_cent_`year'm`month'
		replace min_year = `year'      if min_pf == PFSE_cent_`year'm`month'
	}
}

// replace cov value with that of min_periodo
local covs pareja anios_educ n_hijos_less18

foreach var in `covs' {
	gen `var' = .
	forval year = 2012/2015 {
		forval month = 12(-1)1 {
			replace `var' = `var'_`year'm`month' if min_month == `month' & min_year == `year'
		}
	}	
}

// qnorm(0.975) = 3.92

foreach depvar in "n_emp" "lw_2"{
	// 1: all, 2: single, 3: married
	* ---------------------- PANEL A: OVERALL ---------------------- *
	// PANEL A: ALL
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') //if pareja == 0

	local n_`depvar'_1_a    = `r(N)'
	local beta_`depvar'_1_a = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_1_a   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_1_a = string(round(r(mean),0.001),"%9.3f")

	// PANEL A: SINGLE
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if pareja == 0
	
	local n_`depvar'_2_a    = `r(N)'
	local beta_`depvar'_2_a = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_2_a   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_2_a = string(round(r(mean),0.001),"%9.3f")

	// PANEL A: MARRIED
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if pareja == 1
	
	local n_`depvar'_3_a    = `r(N)'
	local beta_`depvar'_3_a = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_3_a   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_3_a = string(round(r(mean),0.001),"%9.3f")
	
	* ---------------------- PANEL B: HAS CHILDREN UNDER 18 ---------------------- *
	// PANEL B: ALL
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if n_hijos_les18>0
 
	local n_`depvar'_1_b    = `r(N)'
	local beta_`depvar'_1_b = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_1_b   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_1_b = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL B: SINGLE 
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if n_hijos_les18>0 & pareja == 0
 
	local n_`depvar'_2_b    = `r(N)'
	local beta_`depvar'_2_b = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_2_b   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_2_b = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL B: MARRIED
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if n_hijos_les18>0 & pareja == 1
 
	local n_`depvar'_3_b    = `r(N)'
	local beta_`depvar'_3_b = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_3_b   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_3_b = string(round(r(mean),0.001),"%9.3f")

	* ---------------------- PANEL C: 12 YEARS OR LESS OF EDUCATION ---------------------- *
	// PANEL C: ALL
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if anios_educ <= 12
 
	local n_`depvar'_1_c    = `r(N)'
	local beta_`depvar'_1_c = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_1_c   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_1_c = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL C: SINGLE 
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if anios_educ <= 12 & pareja == 0
 
	local n_`depvar'_2_c    = `r(N)'
	local beta_`depvar'_2_c = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_2_c   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_2_c = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL C: MARRIED
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if anios_educ <= 12 & pareja == 1
 
	local n_`depvar'_3_c    = `r(N)'
	local beta_`depvar'_3_c = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_3_c   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_3_c = string(round(r(mean),0.001),"%9.3f")
	
	* ---------------------- PANEL D: 12 YEARS OR LESS OF EDUCATION OR HAS CHILDREN UNDER 18 ---------------------- *
	// PANEL D: ALL
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if anios_educ <= 12 & n_hijos_less18 > 0 
 
	local n_`depvar'_1_d    = `r(N)'
	local beta_`depvar'_1_d = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_1_d   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_1_d = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL D: SINGLE 
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if anios_educ <= 12 & n_hijos_less18 > 0 & pareja == 0
 
	local n_`depvar'_2_d    = `r(N)'
	local beta_`depvar'_2_d = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_2_d   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_2_d = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL D: MARRIED
	qui: rdrandinf `depvar' d_eleg_ever, wl(`leftw') wr(`rightw') if anios_educ <= 12 & n_hijos_less18 > 0 & pareja == 1
 
	local n_`depvar'_3_d    = `r(N)'
	local beta_`depvar'_3_d = string(round(`r(obs_stat)',0.001),"%9.3f")
	local se_`depvar'_3_d   = string(round((`r(ci_ub)'-`r(ci_lb)')/3.92,0.001),"%9.3f")
	qui: sum `depvar'       if e(sample) & min_pf >0
	local mean_`depvar'_3_d = string(round(r(mean),0.001),"%9.3f")
	
}


* --- redo table 
file open table_rdd using "$salida/tablas_graficos/employment_localrand_long_minpfse.tex", write replace
file write table_rdd "\begin{tabular}{lcccccccc}" _n //9 cols
file write table_rdd "\toprule" _n
file write table_rdd "                    & All          & Single       & Married      &&& All         & Single      & Married \\ \hline \hline" _n
file write table_rdd "\multicolumn{9}{c}{Panel A: Overall}\\ \hline"_n
file write table_rdd "                                     & \multicolumn{3}{c}{Employment}  &&&  \multicolumn{3}{c}{log(Earnings)}\\  \hline "_n
file write table_rdd "BTM elegibility     & `beta_n_emp_1_a' & `beta_n_emp_2_a' & `beta_n_emp_3_a' &&& `beta_lw_2_1_a' & `beta_lw_2_2_a' & `beta_lw_2_3_a' \\"_n
file write table_rdd "                    & (`se_n_emp_1_a') & (`se_n_emp_2_a') & (`se_n_emp_3_a') &&& (`se_lw_2_1_a') & (`se_lw_2_2_a') & (`se_lw_2_3_a') \\"_n
file write table_rdd "Nº obs              & `n_n_emp_1_a'    & `n_n_emp_2_a'    & `n_n_emp_3_a'    &&&   `n_lw_2_1_a'  &   `n_lw_2_2_a'  &   `n_lw_2_3_a'  \\"_n
file write table_rdd "Counterfactual mean & `mean_n_emp_1_a' & `mean_n_emp_2_a' & `mean_n_emp_3_a' &&& `mean_lw_2_1_a' & `mean_lw_2_2_a' & `mean_lw_2_3_a' \\"_n
file write table_rdd " &&&&&&&& \\ \hline  \hline "_n
file write table_rdd "\multicolumn{9}{c}{Panel B: Has children under 18}\\  \hline "_n
file write table_rdd "                                     & \multicolumn{3}{c}{Employment}  &&&  \multicolumn{3}{c}{log(Earnings)}\\  \hline "_n
file write table_rdd "BTM elegibility     & `beta_n_emp_1_b' & `beta_n_emp_2_b' & `beta_n_emp_3_b' &&& `beta_lw_2_1_b' & `beta_lw_2_2_b' & `beta_lw_2_3_b' \\"_n
file write table_rdd "                    & (`se_n_emp_1_b') & (`se_n_emp_2_b') & (`se_n_emp_3_b') &&& (`se_lw_2_1_b') & (`se_lw_2_2_b') & (`se_lw_2_3_b') \\"_n
file write table_rdd "Nº obs              & `n_n_emp_1_b'    & `n_n_emp_2_b'    & `n_n_emp_3_b'    &&&   `n_lw_2_1_b'  &  `n_lw_2_2_b'   & `n_lw_2_3_b'    \\"_n
file write table_rdd "Counterfactual mean & `mean_n_emp_1_b' & `mean_n_emp_2_b' & `mean_n_emp_3_b' &&& `mean_lw_2_1_b' & `mean_lw_2_2_b' & `mean_lw_2_3_b' \\"_n
file write table_rdd " &&&&&&&& \\ \hline  \hline"_n
file write table_rdd "\multicolumn{9}{c}{Panel C: 12 or less years of education}\\  \hline"_n
file write table_rdd "                                     & \multicolumn{3}{c}{Employment}  &&&  \multicolumn{3}{c}{log(Earnings)}\\  \hline "_n
file write table_rdd "BTM elegibility     & `beta_n_emp_1_c' & `beta_n_emp_2_c' & `beta_n_emp_3_c' &&& `beta_lw_2_1_c' & `beta_lw_2_2_c' & `beta_lw_2_3_c' \\"_n
file write table_rdd "                    & (`se_n_emp_1_c') & (`se_n_emp_2_c') & (`se_n_emp_3_c') &&& (`se_lw_2_1_c') & (`se_lw_2_2_c') & (`se_lw_2_3_c') \\"_n
file write table_rdd "Nº obs              & `n_n_emp_1_c'    & `n_n_emp_2_c'    & `n_n_emp_3_c'    &&& `n_lw_2_1_c'    & `n_lw_2_2_c'    & `n_lw_2_3_c'    \\"_n
file write table_rdd "Counterfactual mean & `mean_n_emp_1_c' & `mean_n_emp_2_c' & `mean_n_emp_3_c' &&& `mean_lw_2_1_c' & `mean_lw_2_2_c' & `mean_lw_2_3_c' \\"_n
file write table_rdd " &&&&&&&& \\ \hline  \hline "_n
file write table_rdd "\multicolumn{9}{c}{Panel D: Has children under 18 and has 12 or less years of education}\\ \hline"_n
file write table_rdd "                                     & \multicolumn{3}{c}{Employment}  &&&  \multicolumn{3}{c}{log(Earnings)}\\  \hline "_n
file write table_rdd "BTM elegibility     & `beta_n_emp_1_d' & `beta_n_emp_2_d' & `beta_n_emp_3_d' &&& `beta_lw_2_1_d' & `beta_lw_2_2_d' & `beta_lw_2_3_d' \\"_n
file write table_rdd "                    & (`se_n_emp_1_d') & (`se_n_emp_2_d') & (`se_n_emp_3_d') &&& (`se_lw_2_1_d') & (`se_lw_2_2_d') & (`se_lw_2_3_d') \\"_n
file write table_rdd "Nº obs              & `n_n_emp_1_d'    & `n_n_emp_2_d'    & `n_n_emp_3_d'    &&& `n_lw_2_1_d'    & `n_lw_2_2_d'    & `n_lw_2_3_d'    \\"_n
file write table_rdd "Counterfactual mean & `mean_n_emp_1_d' & `mean_n_emp_2_d' & `mean_n_emp_3_d' &&& `mean_lw_2_1_d' & `mean_lw_2_2_d' & `mean_lw_2_3_d' \\"_n
file write table_rdd "\bottomrule" _n
file write table_rdd "\end{tabular}" _n
file close table_rdd 




