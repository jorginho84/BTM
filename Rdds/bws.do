/*
* =========================================================
	project: BTM
	date: 01-07-2023
	objective:  This do-file estimates static treatment effects using different bandwidths (prev Table 4, now Fig ?)
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

sysdir set PLUS "C:\ado\plus"

cap log close
*log using "$lod_dir\log_employment_main.txt", text replace

* ------------------------------------------------------------------------------- *
* ------------------------------- TRABAJO DE BBDD ------------------------------- *
* ------------------------------------------------------------------------------- *

// abrir base
*use  "$salida\rentas_wide_new.dta",clear
use "/Users/antoniaaguilera/Desktop/BTM-paper/data/data_sim.dta", clear

cap drop rem_2011m*

// employment
forvalues y = 2012/2015{
	if `y' == 2012 {
		forvalues m = 7/12{
				gen emp_`y'm`m' = .
				replace emp_`y'm`m' = 0 if rem_`y'm`m' == 0 | rem_`y'm`m' == .
				replace emp_`y'm`m' = 1 if rem_`y'm`m' != 0 & rem_`y'm`m' != .
		}
	}
	else{
		forvalues m = 1/12{
			gen emp_`y'm`m' = .
			replace emp_`y'm`m' = 0 if rem_`y'm`m' == 0 | rem_`y'm`m' == .
			replace emp_`y'm`m' = 1 if rem_`y'm`m' != 0 & rem_`y'm`m' != .	
		}
	}
}

// number of months employed
egen n_emp = rowtotal(emp_*)

// #BW selection
*rdbwselect  emp_2012m1  PFSE_2012m1_cent 
*scalar h_optimo  = e(h_mserd)
scalar h_optimo = 13.3

* ---------------------------------------- *
* -------------- SHARP RDD2 -------------- *
* ---------------------------------------- *

// Using best application to estimate effects of eligibility
/*
forvalues y = 2012/2015{
	forvalues m = 1/12{
		rename PFSE_`y'm`m'_cent PFSE_cent_`y'm`m'
	}
}
*/
 
*drop PFSE_cent_2012m1 PFSE_cent_2012m2 PFSE_cent_2012m3 PFSE_cent_2012m4 PFSE_cent_2012m5 PFSE_cent_2012m6
*egen min_pf = rowmin(PFSE_cent_*)
gen d_eleg_ever = min_pf<= 0

gen min_pf_2 = min_pf^2

// QUITAR EL ROUND
foreach bw of numlist 5 8 13 16 19 22 {
	qui: reg n_emp d_eleg_ever min_pf d_eleg_ever#c.min_pf if min_pf <= `bw' & min_pf >= -`bw', vce(robust)
	local beta1_`bw'  = _b[d_eleg_ever]
	local se1_`bw'    = _se[d_eleg_ever]
	local df1_`bw'    = `e(df_r)'
	
	qui: reg n_emp d_eleg_ever min_pf min_pf_2 d_eleg_ever#c.min_pf d_eleg_ever#c.min_pf_2 if min_pf <= `bw' & min_pf >= -`bw', vce(robust)
	local beta2_`bw' = _b[d_eleg_ever]
	local se2_`bw'   = _se[d_eleg_ever]
	local df2_`bw'   = `e(df_r)'
}


* ---------------------------- *
* ---------- GRAPH ----------- *
* ---------------------------- *

// dataset 
*preserve 
clear all 

set obs 6
// bw: 5 8 13 16 19 22
gen     pos_1 = 1     if _n == 1
gen     pos_2 = 2.5   if _n == 1
replace pos_1 = 6     if _n == 2
replace pos_2 = 7.5   if _n == 2 
replace pos_1 = 11    if _n == 3 
replace pos_2 = 12.5  if _n == 3 
replace pos_1 = 16    if _n == 4 
replace pos_2 = 17.5  if _n == 4 
replace pos_1 = 21    if _n == 5 
replace pos_2 = 22.5  if _n == 5 
replace pos_1 = 26    if _n == 6
replace pos_2 = 27.5  if _n == 6

/*
foreach var in beta1 beta2 se1 se2 df1 df2 {
	gen     `var' = ``var'_5'  if _n == 1
	replace `var' = ``var'_8'  if _n == 2
	replace `var' = ``var'_13' if _n == 3
	replace `var' = ``var'_16' if _n == 4
	replace `var' = ``var'_19' if _n == 5
	replace `var' = ``var'_22' if _n == 6
}
*/


* ------- BORRAR ESTO DESPUÉS ----- *
set seed 13231
foreach var in beta1 beta2 se1 se2 df1 df2 {
	gen     `var' = runiform() if _n == 1
	replace `var' = runiform() if _n == 2
	replace `var' = runiform() if _n == 3
	replace `var' = runiform() if _n == 4
	replace `var' = runiform() if _n == 5
	replace `var' = runiform() if _n == 6
}
* ------- BORRAR ESTO DESPUÉS ----- *



// confidence intervals 
foreach x in 1 2 {
	// ci_upper
	gen     ci_upper`x' = beta`x' + invttail(df`x' , 0.05)*se`x'  if _n == 1
	replace ci_upper`x' = beta`x' + invttail(df`x' , 0.05)*se`x'  if _n == 2
	replace ci_upper`x' = beta`x' + invttail(df`x' , 0.05)*se`x'  if _n == 3
	replace ci_upper`x' = beta`x' + invttail(df`x' , 0.05)*se`x'  if _n == 4
	replace ci_upper`x' = beta`x' + invttail(df`x' , 0.05)*se`x'  if _n == 5
	replace ci_upper`x' = beta`x' + invttail(df`x' , 0.05)*se`x'  if _n == 6
	
	// ci_lower
	gen     ci_lower`x' = beta`x' - invttail(df`x' , 0.05)*se`x'  if _n == 1
	replace ci_lower`x' = beta`x' - invttail(df`x' , 0.05)*se`x'  if _n == 2
	replace ci_lower`x' = beta`x' - invttail(df`x' , 0.05)*se`x'  if _n == 3
	replace ci_lower`x' = beta`x' - invttail(df`x' , 0.05)*se`x'  if _n == 4
	replace ci_lower`x' = beta`x' - invttail(df`x' , 0.05)*se`x'  if _n == 5
	replace ci_lower`x' = beta`x' - invttail(df`x' , 0.05)*se`x'  if _n == 6

}

* ---------------------------- *
* ----------- PLOT ----------- *
* ---------------------------- *

tw (scatter  beta1 pos_1, msymbol(circle) msize(large) mcolor(blue*.8) mfcolor(blue*.8)) ///
   (scatter  beta2 pos_2, msymbol(circle) msize(large) mcolor(orange*.8) mfcolor(orange*.8)) ///
   (rcap ci_upper1 ci_lower1 pos_1, lpattern(solid) lcolor(blue*.8))  ///
   (rcap ci_upper2 ci_lower2 pos_2, lpattern(solid) lcolor(orange*.8)), ///
   ytitle("", height(10)) xtitle("Bandwidth") legend(off) ///
   xlabel( 1.75 "5" 6.75 "8" 11.75 "13" 16.75 "16" 21.75 "19" 26.75 "22") ///
   ylabel(, labgap(2) nogrid angle(0))  ///
   graphregion(fcolor(white) ifcolor(white) lcolor(white) ilcolor(white)) plotregion(fcolor(white) lcolor(white)  ifcolor(white) ilcolor(white))  ///
   scheme(s2mono) yline(0, lpattern(dash) lcolor(black)) scale(1.8)

graph export "$salida/bw.pdf", as(pdf) replace

