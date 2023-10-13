/*
This do-file creates a data set for pyhton (structural estimation)

*/


/*
This do-file estimates static treatment effects, employment and earnings

*/


clear all
clear matrix
clear mata
set more off
set maxvar 100000



*--------------------- GLOBALES: UBICACION DE ARCHIVOS  ---------------------*
  global entrada "\\nas05\Repositorio_Datos_ADM\07_BASES_INN\02_RIS_INVESTIGACION\RIS_INVESTIGACION_2\01_UANDES_EFECTO_SUBISIDO_CONTRATACION_EMPLEO_FEMENINO\02_DATOS_ENTRADA\12_BTM\Ejercicios"

	global dir_graph "R:\04_RESULTADOS\New Graph"
	global results "R:\04_RESULTADOS"
	
	global salida "R:\03_DATOS_SALIDA"

	global salida2 "C:\Users\ris_schavez\Desktop\SALIDA"
	
	global log_dir "R:\05_RESPALDO_ALGORITMOS\log_file"

*--------------------- BASES A USAR  ---------------------*
sysdir set PLUS "C:\ado\plus"

cap log close
*log using "$lod_dir\log_employment_main.txt", text replace

use  "$salida\rentas_wide_new.dta",clear
drop rem_2011m* rem_2013m* rem_2014m* rem_2015m*

forvalues m = 7/12{
	replace rem_`y'm`m' = . if rem_`y'm`m' == 0
	gen emp_`y'm`m' = .
	replace emp_`y'm`m' = 0 if rem_`y'm`m' == .
	replace emp_`y'm`m' = 1 if rem_`y'm`m' != 0 & rem_`y'm`m' != .
	
}

egen employment = rowmean(emp_2012m7 emp_2012m8 emp_2012m9 emp_2012m10 emp_2012m11 emp_2012m12)

*Earnings for monthly earnings > 0
egen earnings = rowmean(rem_2012m7 rem_2012m8 rem_2012m9 rem_2012m10 rem_2012m11 rem_2012m12)

*Best Score
forvalues y = 2012/2015{
	forvalues m = 1/12{
		rename PFSE_`y'm`m'_cent PFSE_cent_`y'm`m'
	
	}

}
drop PFSE_cent_2012m1 PFSE_cent_2012m2 PFSE_cent_2012m3 PFSE_cent_2012m4 PFSE_cent_2012m5 PFSE_cent_2012m6 /*
*/ PFSE_cent_2013* PFSE_cent_2014* PFSE_cent_2015*
egen pfse = rowmin(PFSE_cent_*)
gen d_eleg = min_pf<= 0

*Covariates measured at 2012, before program began
rename (anios_educ_2012m1 n_hijos_2012m1 n_hijos_menores_2012m1 pareja_2012m1) (anios_educ n_hijos n_hijos_menores pareja)
replace pareja = 0 if pareja==.

*Age at 2012
gen edad = 2012 - yearbirth


keep employment earnings pfse d_eleg anios_educ n_hijos n_hijos_menores pareja edad

*Save data in MDS computer here





