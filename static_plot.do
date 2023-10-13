/*
* =========================================================
	project: BTM
	date: 10-08-2023
	objective: This do-file estimates static treatment 
	effects, employment and earnings
	running var:
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

// abrir base 
use  "$salida\rentas_wide_new.dta",clear
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

drop PFSE_cent_2012m1 PFSE_cent_2012m2 PFSE_cent_2012m3 PFSE_cent_2012m4 PFSE_cent_2012m5 PFSE_cent_2012m6

egen mean_pf = rowmean(PFSE_cent_*)
gen d_eleg_ever = mean_pf<= 0

* ---------------------------------------- *
* --------- HETEROGENEOUS EFFECTS -------- *
* ---------------------------------------- *

gen wichdate = ""
local dates PFSE_cent_2012m7 PFSE_cent_2012m8 PFSE_cent_2012m9 PFSE_cent_2012m10 PFSE_cent_2012m11 PFSE_cent_2012m12 ///
PFSE_cent_2013m1 PFSE_cent_2013m2 PFSE_cent_2013m3 PFSE_cent_2013m4 PFSE_cent_2013m5 PFSE_cent_2013m6 PFSE_cent_2013m7 PFSE_cent_2013m8 PFSE_cent_2013m9 PFSE_cent_2013m10 PFSE_cent_2013m11 PFSE_cent_2013m12 ///
PFSE_cent_2014m1 PFSE_cent_2014m2 PFSE_cent_2014m3 PFSE_cent_2014m4 PFSE_cent_2014m5 PFSE_cent_2014m6 PFSE_cent_2014m7 PFSE_cent_2014m8 PFSE_cent_2014m9 PFSE_cent_2014m10 PFSE_cent_2014m11 PFSE_cent_2014m12 ///
PFSE_cent_2015m1 PFSE_cent_2015m2 PFSE_cent_2015m3 PFSE_cent_2015m4 PFSE_cent_2015m5 PFSE_cent_2015m6 PFSE_cent_2015m7 PFSE_cent_2015m8 PFSE_cent_2015m9 PFSE_cent_2015m10 PFSE_cent_2015m11 PFSE_cent_2015m12

quietly foreach v in `dates' {
	replace wichdate = cond(missing(wichdate), "`v'", wichdate + " `v'") if `v' == mean_pf
}

gen mean_pf_date = substr(wichdate,11,7)
replace mean_pf_date = subinstr(mean_pf_date, " ", "",.)
drop wichdate

local covariates1 ingreso_anual anios_educ n_hijos n_hijos_menores n_hijos_less6 pareja ingreso_lab_h c_parentesco
foreach v in `covariates1'{
	local covariates_`v' `v'_2012m1 `v'_2012m2 `v'_2012m3 `v'_2012m4 `v'_2012m5 `v'_2012m6 `v'_2012m7 `v'_2012m8 `v'_2012m9 `v'_2012m10 `v'_2012m11 `v'_2012m12 ///
`v'_2013m1 `v'_2013m2 `v'_2013m3 `v'_2013m4 `v'_2013m5 `v'_2013m6 `v'_2013m7 `v'_2013m8 `v'_2013m9 `v'_2013m10 `v'_2013m11 `v'_2013m12 ///
`v'_2014m1 `v'_2014m2 `v'_2014m3 `v'_2014m4 `v'_2014m5 `v'_2014m6 `v'_2014m7 `v'_2014m8 `v'_2014m9 `v'_2014m10 `v'_2014m11 `v'_2014m12 ///
`v'_2015m1 `v'_2015m2 `v'_2015m3 `v'_2015m4 `v'_2015m5 `v'_2015m6 `v'_2015m7 `v'_2015m8 `v'_2015m9 `v'_2015m10 `v'_2015m11 `v'_2015m12
}

* aca rescato la covariable que tiene el individuo en la misma fecha que tiene el menor puntaje, por ejemplo si el individuo tiene el menor puntaje en 2013m5, le pongo a ese individuo las caracteristicas que tenia en esa fecha. Despues al otro con su fecha respectiva y asi...
foreach v in `covariates1'{
	gen `v'=.
	foreach v2 in `covariates_`v''{
		quietly replace `v' = `v2' if "`v2'" == "`v'"+"_"+mean_pf_date
	}
}
replace pareja = 0 if pareja==.


foreach depvar in "n_emp" "lw_2"{
	// 1: all, 2: single, 3: married
	* ---------------------- PANEL A: OVERALL ---------------------- *
	// PANEL A: ALL
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo, vce(robust)
	local n_`depvar'_1_a = e(N)
	local beta_`depvar'_1_a = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_1_a = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar' if e(sample) & mean_pf >0
	local mean_`depvar'_1_a = string(round(r(mean),0.001),"%9.3f")

	// PANEL A: SINGLE
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & pareja == 0, vce(robust)
	local n_`depvar'_2_a = e(N)
	local beta_`depvar'_2_a = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_2_a = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar' if e(sample) & mean_pf >0
	local mean_`depvar'_2_a = string(round(r(mean),0.001),"%9.3f")

	// PANEL A: MARRIED
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & pareja == 1, vce(robust)
	local n_`depvar'_3_a = e(N)
	local beta_`depvar'_3_a = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_3_a = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar' if_a e(sample) & mean_pf >0
	local mean_`depvar'_3_a = string(round(r(mean),0.001),"%9.3f")
	
	* ---------------------- PANEL B: HAS CHILDREN UNDER 18 ---------------------- *
	// PANEL B: ALL
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & n_hijos_less18 > 0, vce(robust)
	local n_`depvar'_1_b = e(N)
	local beta_`depvar'_1_b = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_1_b = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar' if e(sample) & mean_pf >0
	local mean_`depvar'_1_b = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL B: SINGLE 
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & n_hijos_less18 > 0 & pareja == 0, vce(robust)
	local n_`depvar'_2_b = e(N)
	local beta_`depvar'_2_b = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_2_b = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar' if e(sample) & mean_pf >0
	local mean_`depvar'_2_b = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL B: MARRIED
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & n_hijos_less18 > 0 & pareja == 1, vce(robust)
	local n_`depvar'_3_b = e(N)
	local beta_`depvar'_3_b = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_3_b = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar' if e(sample) & mean_pf >0
	local mean_`depvar'_3_b = string(round(r(mean),0.001),"%9.3f")

	* ---------------------- PANEL C: 12 YEARS OR LESS OF EDUCATION ---------------------- *
	// PANEL C: ALL
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & anios_educ <= 12, vce(robust)
	local n_`depvar'_1_c = e(N)
	local beta_`depvar'_1_c = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_1_c = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar'  e(sample) & mean_pf >0
	local mean_`depvar'_1_c = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL C: SINGLE 
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & anios_educ <= 12 & pareja == 0, vce(robust)
	local n_`depvar'_2_c = e(N)
	local beta_`depvar'_2_c = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_2_c = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar'  e(sample) & mean_pf >0
	local mean_`depvar'_2_c = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL C: MARRIED
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & anios_educ <= 12 & pareja == 1, vce(robust)
	local n_`depvar'_3_c = e(N)
	local beta_`depvar'_3_c = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_3_c = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar'  e(sample) & mean_pf >0
	local mean_`depvar'_3_c = string(round(r(mean),0.001),"%9.3f")
	
	* ---------------------- PANEL D: 12 YEARS OR LESS OF EDUCATION OR HAS CHILDREN UNDER 18 ---------------------- *
	// PANEL D: ALL
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & anios_educ <= 12 & n_hijos_less18 > 0, vce(robust)
	local n_`depvar'_1_d = e(N)
	local beta_`depvar'_1_d = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_1_d = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar'  e(sample) & mean_pf >0
	local mean_`depvar'_1_d = string(round(r(mean),0.001),"%9.3f")

	// PANEL D: SINGLE 
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & anios_educ <= 12 & n_hijos_less18 > 0 & pareja == 0, vce(robust)
	local n_`depvar'_2_d = e(N)
	local beta_`depvar'_2_d = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_2_d = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar'  e(sample) & mean_pf >0
	local mean_`depvar'_2_d = string(round(r(mean),0.001),"%9.3f")
	
	// PANEL D: MARRIED
	qui:reg `depvar' d_eleg_ever mean_pf d_eleg_ever#c.mean_pf if mean_pf <= h_optimo & mean_pf >= -h_optimo & anios_educ <= 12 & n_hijos_less18 > 0 & pareja == 1, vce(robust)
	local n_`depvar'_3_d = e(N)
	local beta_`depvar'_3_d = string(round(_b[d_eleg_ever],0.001),"%9.3f")
	local se_`depvar'_3_d = string(round(_se[d_eleg_ever],0.001),"%9.3f")
	qui: sum `depvar'  e(sample) & mean_pf >0
	local mean_`depvar'_3_d = string(round(r(mean),0.001),"%9.3f")
	
}

* -------- create data base

clear all 

set obs 
