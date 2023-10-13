************
* CASEN - Parameters 
* Income function

************

local user pjdea

if "`user'" == "pjdea"{
    global btm "C:\Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\Stata btm\casen2015"
	global data "${btm}\Data"
	global Result "${btm}\Results"
	global Tex "${btm}\Tex"
	global Graphs "${btm}\Graph"
}

clear
set more off

use "$data\Casen 2015"

* 1. calcular ingreso total para hogares con mujeres 
* en la edad que corresponde al btm (25-59 años), con la ecuación:
*  Y_tot = ingresos totales del hogar - ingresos por BTM

gen y2506_1 = .
replace y2506_1 = y2506 if y2506 != .
replace y2506_1 = 0 if y2506 == .

gen y_tot = ln(ytoth - y2506_1)

* 2. regresión para mujeres que trabajan en la edad que corresponde al btm
* (25-59 años) con las siguientes condiciones:
* 2.a. mujeres casadas y no casadas
* 2.b. cantidad de hijos 0, 1, 2 y >=3
* log(Y_tot) = a + b*ingresos laborales + error

*3. regresión para mujeres que no trabajan en la edad que corresponde al btm
* (25-59 años) con las siguientes condiciones:
* 3.a. mujeres casadas y no casadas
* 3.b. cantidad de hijos 0, 1, 2 y >=3
* Y_tot = promedio de ingresos totales hogar para mujeres que no trabajan

*4. recuperar el valor de los parámetros buscados
* para cada una de las condiciones descritas. 

gen hijos = .
replace hijos = 0 if s4 == 0
replace hijos = 1 if s4 == 1
replace hijos = 2 if s4 == 2
replace hijos = 3 if s4 >= 3
replace hijos = . if s4 == .
replace hijos = . if s4 == 99

gen y_sal = ln(y0101)

* # escala de beta

foreach i in 0 1 2 3 {
	
	*#1 MARRIED -- WORKING
	* # Estado civil == considero conviviente civil pareja (unión civil)
	* # persona
	reg y_tot y_sal if (sexo == 2) & (ecivil == 1 | ecivil == 2 | ecivil == 3) & (edad > 24 & edad < 60) & (activ == 1) & (hijos == `i') 
	* # No redondiar
	local b_1_`i' = string(round(_b[y_sal],.001),"%9.3f")
	local alpha_1_`i' = string(round(_b[_cons],.001),"%9.3f")
	
	*#2 NOT MARRIED -- WORKING
	reg y_tot y_sal if (sexo == 2) & (ecivil != 1 | ecivil != 2 | ecivil != 3) & (edad > 24 & edad < 60) & (activ == 1) & (hijos == `i')

	local b_2_`i' = string(round(_b[y_sal],.001),"%9.3f")
	local alpha_2_`i' = string(round(_b[_cons],.001),"%9.3f")
	
	*#3 MARRIED -- NOT WORKING
	* # Buscando empleo ... agregar
	egen ym1_tot_`i' = mean(y_tot) if (sexo == 2) & (ecivil == 1 | ecivil == 2 | ecivil == 3) & (edad > 24 & edad < 60) & (activ == 2 | activ == 3) & (hijos == `i')

	local z_1_`i' = string(round(r(mean),.001),"%9.3f")
	
	*#4	NOT MARRIED -- NOT WORKING
	egen ym2_tot_`i' = mean(y_tot) if (sexo == 2) & (ecivil != 1  ecivil != 2 | ecivil != 3) & (edad > 24 & edad < 60) & (activ == 2 | activ == 3) & (hijos == `i')

	local z_2_`i' = string(round(r(mean),.001),"%9.3f")

	}	
	
	
*** EXCEL: parameters python ***

putexcel set "C:\Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\Stata btm\casen2015\Results\param_python.xlsx", sheet("param") modify

*** MARRIED ***
putexcel E7= `b_1_0', nformat(number_d2)
putexcel E6= `alpha_1_0', nformat(number_d2)
putexcel F7= `b_1_1', nformat(number_d2)
putexcel F6= `alpha_1_1', nformat(number_d2)
putexcel G7= `b_1_2', nformat(number_d2)
putexcel G6= `alpha_1_2', nformat(number_d2)
putexcel H7= `b_1_3', nformat(number_d2)
putexcel H6= `alpha_1_3', nformat(number_d2)
putexcel E8= `z_1_0', nformat(number_d2)
putexcel F8= `z_1_1', nformat(number_d2)
putexcel G8= `z_1_2', nformat(number_d2)
putexcel H8= `z_1_3', nformat(number_d2)
*** NOT MARRIED ***
putexcel E12= `b_2_0', nformat(number_d2)
putexcel E11= `alpha_2_0', nformat(number_d2)
putexcel F12= `b_2_1', nformat(number_d2)
putexcel F11= `alpha_2_1', nformat(number_d2)
putexcel G12= `b_2_2', nformat(number_d2)
putexcel G11= `alpha_2_2', nformat(number_d2)
putexcel H12= `b_2_3', nformat(number_d2)
putexcel H11= `alpha_2_3', nformat(number_d2)
putexcel E13= `z_2_0', nformat(number_d2)
putexcel F13= `z_2_1', nformat(number_d2)
putexcel G13= `z_2_2', nformat(number_d2)
putexcel H13= `z_2_3', nformat(number_d2)

*graph twoway (lfit y_tot y_sal) (scatter y_tot y_sal) if hijos == 3

