/*
* =========================================================
	project: BTM
	date: 01-07-2023
	objective:  CREATE SIMULATED DATA TO TEST CODES
* =========================================================
*/

* ------------------------------------------------------------------------------- *
* ----------------------------- CREAR DATA SIMULADA ----------------------------- *
* ------------------------------------------------------------------------------- *
*generate ui = floor((b–a+1)*runiform() + a)
clear all
set obs 500000


// rem y covs
forvalues y = 2011/2015{

	forvalues m = 1/12{
		gen rem_`y'm`m' = floor((2000000-100000+1)*runiform()+100000)	
			
		gen ingreso_anual_`y'm`m' = floor((50-1+1)*runiform()+1)
		replace ingreso_anual_`y'm`m' = ingreso_anual_`y'm`m'*100000
		replace ingreso_anual_`y'm`m' = log(ingreso_anual_`y'm`m')
		
		gen     ingreso_lab_h_`y'm`m' = floor((50-1+1)*runiform()+1)
		replace ingreso_lab_h_`y'm`m' = ingreso_anual_`y'm`m'*100000
		replace ingreso_lab_h_`y'm`m' = log(ingreso_anual_`y'm`m')
			
		gen anios_educ_`y'm`m' = floor((17-6+1)*runiform()+6)
		
		gen n_hijos_`y'm`m' = floor((3-0+1)*runiform()+0)
		gen n_hijos_less18_`y'm`m' = floor((3-0+1)*runiform()+0)
			
		gen n_hijos_menores_`y'm`m' = floor((3-0+1)*runiform()+0)
		replace n_hijos_menores_`y'm`m' = 0 if n_hijos_`y'm`m'<n_hijos_menores_`y'm`m'
			
		gen pareja_`y'm`m' = floor((1-0+1)*runiform()+0)
		gen c_parentesco_`y'm`m' = floor((7-1+1)*runiform()+7)

	}
}


forvalues y = 2012/2015{
	forvalues m = 1/12{
		gen PFSE_`y'm`m'_cent = floor((15+15+1)*runiform()-15)		
	}
}


save "/Users/antoniaaguilera/Desktop/BTM-paper/data/data_sim.dta", replace 



stop 
	if `y' == 2012 {
		forvalues m = 7/12 {
			gen rem_`y'm`m' = floor((2000000-100000+1)*runiform()+100000)	
			
			gen ingreso_anual_`y'm`m' = floor((50-1+1)*runiform()+1)
			replace ingreso_anual_`y'm`m' = ingreso_anual_`y'm`m'*100000
			replace ingreso_anual_`y'm`m' = log(ingreso_anual_`y'm`m')
			
			gen anios_educ_`y'm`m' = floor((17-6+1)*runiform()+6)
			
			gen n_hijos_`y'm`m' = floor((3-0+1)*runiform()+0)
			
			gen n_hijos_menores_`y'm`m' = floor((3-0+1)*runiform()+0)
			replace n_hijos_menores_`y'm`m' = 0 if n_hijos_`y'm`m'<n_hijos_menores_`y'm`m'
			
			gen pareja`y'm`m' = floor((1-0+1)*runiform()+1)

		}
	}
