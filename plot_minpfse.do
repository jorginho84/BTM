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
	egen n_emp_`y' = rowtotal(emp_`y'*)
}
 
// #BW selection
*rdbwselect  emp_2012m1  PFSE_2012m1_cent 
*scalar h_optimo  = e(h_mserd)
scalar h_optimo = 13.3

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

* ---------------------------------------- *
* -------------- SHARP RDD2 -------------- *
* ---------------------------------------- *

// Using best application to estimate effects of eligibility 

forvalues y = 2012/2015{
	forvalues m = 1/12{
		rename PFSE_`y'm`m'_cent PFSE_cent_`y'm`m'	
	}
}

// 2012
egen min_pf_2012 = rowmin(PFSE_cent_2012*)
gen d_eleg_2012   = min_pf_2012 <= 0

* ---------------------------------------- *
* --------- HETEROGENEOUS EFFECTS -------- *
* ---------------------------------------- *
// conservar el valor del mes donde el PFSE es el más bajo (el que gatilla elegibilidad)
gen min_mes = . 

forval x = 12(-1)1 {
	replace min_mes = `x' if min_pf_2012 == PFSE_cent_2012m`x'
}

// replace cov value with that of min_periodo
local covs pareja anios_educ n_hijos_less18
forval x = 1/12 {
	foreach var in `covs' {
		gen `var' = `var'_2012m`x' if min_mes = `x'
	}
	
}


forval year = 2012/2015 {
	// 1: all, 2: single, 3: married
	* ---------------------- PANEL A: OVERALL ---------------------- *
	// PANEL A: ALL
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo, vce(robust)
	local n_n_emp_`year'_1_a    = e(N)
	local beta_n_emp_`year'_1_a = _b[d_eleg_2012]
	local se_n_emp_`year'_1_a   = _se[d_eleg_2012]
	local df_n_emp_`year'_1_a   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_1_a = r(mean)

	// PANEL A: SINGLE
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & pareja_2012 == 0, vce(robust)
	local n_n_emp_`year'_2_a    = e(N)
	local beta_n_emp_`year'_2_a = _b[d_eleg_2012]
	local se_n_emp_`year'_2_a   = _se[d_eleg_2012]
	local df_n_emp_`year'_2_a   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_2_a = r(mean)

	// PANEL A: MARRIED
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & pareja_2012 == 1, vce(robust)
	local n_n_emp_`year'_3_a    = e(N)
	local beta_n_emp_`year'_3_a = _b[d_eleg_2012]
	local se_n_emp_`year'_3_a   = _se[d_eleg_2012]
	local df_n_emp_`year'_3_a   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_3_a = r(mean)
	  
	* ---------------------- PANEL B: HAS CHILDREN UNDER 18 ---------------------- *
	// PANEL B: ALL
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & n_hijos_less18_2012 > 0, vce(robust)
	local n_n_emp_`year'_1_b    = e(N)
	local beta_n_emp_`year'_1_b = _b[d_eleg_2012]
	local se_n_emp_`year'_1_b   = _se[d_eleg_2012]
	local df_n_emp_`year'_1_b   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_1_b = r(mean)
	
	// PANEL B: SINGLE 
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & n_hijos_less18_2012 > 0 & pareja_2012 == 0, vce(robust)
	local n_n_emp_`year'_2_b    = e(N)
	local beta_n_emp_`year'_2_b = _b[d_eleg_2012]
	local se_n_emp_`year'_2_b   = _se[d_eleg_2012]
	local df_n_emp_`year'_2_b   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_2_b = r(mean)
	
	// PANEL B: MARRIED
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & n_hijos_less18_2012 > 0 & pareja_2012 == 1, vce(robust)
	local n_n_emp_`year'_3_b    = e(N)
	local beta_n_emp_`year'_3_b = _b[d_eleg_2012]
	local se_n_emp_`year'_3_b   = _se[d_eleg_2012]
	local df_n_emp_`year'_3_b   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_3_b = r(mean)

	* ---------------------- PANEL C: 12 YEARS OR LESS OF EDUCATION ---------------------- *
	// PANEL C: ALL
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & anios_educ_2012 <= 12, vce(robust)
	local n_n_emp_`year'_1_c    = e(N)
	local beta_n_emp_`year'_1_c = _b[d_eleg_2012]
	local se_n_emp_`year'_1_c   = _se[d_eleg_2012]
	local df_n_emp_`year'_1_c   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_1_c = r(mean)
	
	// PANEL C: SINGLE 
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & anios_educ_2012 <= 12 & pareja_2012 == 0, vce(robust)
	local n_n_emp_`year'_2_c    = e(N)
	local beta_n_emp_`year'_2_c = _b[d_eleg_2012]
	local se_n_emp_`year'_2_c   = _se[d_eleg_2012]
	local df_n_emp_`year'_2_c   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_2_c = r(mean)
	
	// PANEL C: MARRIED
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & anios_educ_2012 <= 12 & pareja_2012 == 1, vce(robust)
	
	local n_n_emp_`year'_3_c    = e(N)
	local beta_n_emp_`year'_3_c = _b[d_eleg_2012]
	local se_n_emp_`year'_3_c   = _se[d_eleg_2012]
	local df_n_emp_`year'_3_c   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_3_c = r(mean)
	 
	* ---------------------- PANEL D: 12 YEARS OR LESS OF EDUCATION AND HAS CHILDREN UNDER 18 ---------------------- *
	// PANEL D: ALL
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & anios_educ_2012 <= 12 & n_hijos_less18_2012 > 0, vce(robust)
	local n_n_emp_`year'_1_d    = e(N)
	local beta_n_emp_`year'_1_d = _b[d_eleg_2012]
	local se_n_emp_`year'_1_d   = _se[d_eleg_2012] 
	local df_n_emp_`year'_1_d   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_1_d = r(mean)
 
	// PANEL D: SINGLE 
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & anios_educ_2012 <= 12 & n_hijos_less18_2012 > 0 & pareja_2012 == 0, vce(robust)
	local n_n_emp_`year'_2_d    = e(N)
	local beta_n_emp_`year'_2_d = _b[d_eleg_2012]
	local se_n_emp_`year'_2_d   = _se[d_eleg_2012]
	local df_n_emp_`year'_2_d   = `e(df_r)'
	qui: sum n_emp_`year' 		if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_2_d = r(mean)
	
	// PANEL D: MARRIED
	qui:reg n_emp_`year' d_eleg_2012 min_pf_2012 d_eleg_2012#c.min_pf_2012 if min_pf_2012 <= h_optimo & min_pf_2012 >= -h_optimo & anios_educ_2012 <= 12 & n_hijos_less18_2012 > 0 & pareja_2012 == 1, vce(robust)
	local n_n_emp_`year'_3_d    = e(N)
	local beta_n_emp_`year'_3_d = _b[d_eleg_2012]
	local se_n_emp_`year'_3_d   = _se[d_eleg_2012]
	local df_n_emp_`year'_3_d   = `e(df_r)'
	qui: sum n_emp_`year'       if e(sample) & min_pf_2012 >0
	local mean_n_emp_`year'_3_d = r(mean)
	
}


* ---------------------------------------- *
* ----------------- PLOT ----------------- *
* ---------------------------------------- *

clear all 

set obs 4
// year 2012 
gen     pos_1 = 1   if _n == 1
gen     pos_2 = 2   if _n == 1
gen     pos_3 = 3   if _n == 1
// year 2013
replace pos_1 = 5   if _n == 2
replace pos_2 = 6   if _n == 2 
replace pos_3 = 7   if _n == 2 
// year  2014 
replace pos_1 = 9   if _n == 3 
replace pos_2 = 10  if _n == 3 
replace pos_3 = 11  if _n == 3 
// year 2015
replace pos_1 = 13  if _n == 4 
replace pos_2 = 14  if _n == 4 
replace pos_3 = 15  if _n == 4 

gen     year = 2012 if _n == 1
replace year = 2013 if _n == 2
replace year = 2014 if _n == 3
replace year = 2015 if _n == 4

foreach var in beta_n_emp se_n_emp df_n_emp {
	forval x = 1/3 {
		foreach y in a b c d {
			gen     `var'_`x'_`y' = ``var'_2012_`x'_`y''  if _n == 1
			replace `var'_`x'_`y' = ``var'_2013_`x'_`y''  if _n == 2
			replace `var'_`x'_`y' = ``var'_2014_`x'_`y''  if _n == 3
			replace `var'_`x'_`y' = ``var'_2015_`x'_`y''  if _n == 4
		}
		
	}
}

// confidence intervals 
forval x = 1/3 {
	foreach y in a b c d {
	// ci_upper
	gen     ci_upper_`x'_`y' = beta_n_emp_`x'_`y' + invttail(df_n_emp_`x'_`y' , 0.05)*se_n_emp_`x'_`y'  if _n == 1
	replace ci_upper_`x'_`y' = beta_n_emp_`x'_`y' + invttail(df_n_emp_`x'_`y' , 0.05)*se_n_emp_`x'_`y'  if _n == 2
	replace ci_upper_`x'_`y' = beta_n_emp_`x'_`y' + invttail(df_n_emp_`x'_`y' , 0.05)*se_n_emp_`x'_`y'  if _n == 3
	replace ci_upper_`x'_`y' = beta_n_emp_`x'_`y' + invttail(df_n_emp_`x'_`y' , 0.05)*se_n_emp_`x'_`y'  if _n == 4
	 
	// ci_lower
	gen     ci_lower_`x'_`y' = beta_n_emp_`x'_`y' - invttail(df_n_emp_`x'_`y' , 0.05)*se_n_emp_`x'_`y'  if _n == 1
	replace ci_lower_`x'_`y' = beta_n_emp_`x'_`y' - invttail(df_n_emp_`x'_`y' , 0.05)*se_n_emp_`x'_`y'  if _n == 2
	replace ci_lower_`x'_`y' = beta_n_emp_`x'_`y' - invttail(df_n_emp_`x'_`y' , 0.05)*se_n_emp_`x'_`y'  if _n == 3
	replace ci_lower_`x'_`y' = beta_n_emp_`x'_`y' - invttail(df_n_emp_`x'_`y' , 0.05)*se_n_emp_`x'_`y'  if _n == 4

	}
}


local mean_a "overall"
local mean_b "kidsunder18"
local mean_c "educunder12"
local mean_d "kidsunder18_educunder12"

foreach x in a b c d {
	tw (scatter  beta_n_emp_1_`x' pos_1, msymbol(circle) msize(large) mcolor(blue*.8) mfcolor(blue*.8))      ///
	   (scatter  beta_n_emp_2_`x' pos_2, msymbol(diamond) msize(large) mcolor(orange*.8) mfcolor(orange*.8))  ///
	   (scatter  beta_n_emp_3_`x' pos_3, msymbol(triangle) msize(large) mcolor(green*.8) mfcolor(green*.8)) ///
	   (rcap ci_upper_1_`x' ci_lower_1_`x' pos_1, lpattern(solid) lcolor(blue*.8))    ///
	   (rcap ci_upper_2_`x' ci_lower_2_`x' pos_2, lpattern(solid) lcolor(orange*.8))  ///
	   (rcap ci_upper_3_`x' ci_lower_3_`x' pos_3, lpattern(solid) lcolor(green*.8)), ///
	   ytitle("Employment (# of months)", height(5)) xtitle("Year") ///
	   xlabel( 2 "2012" 6 "2013" 10 "2014" 14 "2015") ///
	   ylabel(, labgap(2) nogrid angle(0))  ///
	   legend(order(1 "All" 2 "Single" 3 "Married") rows(1)) ///
	   graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  ///
	   scheme(s2mono) yline(0, lpattern(dash) lcolor(black)) scale(1.2) saving(`x'.gph,replace)	
	   
	   graph export "$salida/emp_min_`name_`x''.pdf", as(pdf) replace
}



