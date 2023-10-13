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
	global graph "${btm}\Graph"
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

gen index_btm = 0
replace index_btm = 1 if y2506_1 != 0

gen y_sal = ln(y0101)


foreach i in 0 1 2 3 {
	
	*#1 BTM MARRIED
	reg y_tot y_sal if (sexo == 2) & (ecivil == 1) & (edad > 24 & edad < 60) & (activ == 1) & (hijos == `i') & (index_btm == 1)

	local b_1_`i' = string(round(_b[y_sal],.001),"%9.3f")
	local alpha_1_`i' = string(round(_b[_cons],.001),"%9.3f")
	
	*#2 WBTM MARRIED
	reg y_tot y_sal if (sexo == 2) & (ecivil == 1) & (edad > 24 & edad < 60) & (activ == 1) & (hijos == `i') & (index_btm == 0)

	local b_2_`i' = string(round(_b[y_sal],.001),"%9.3f")
	local alpha_2_`i' = string(round(_b[_cons],.001),"%9.3f")
	
	*#3 BTM NOT MARRIED
	reg y_tot y0101h if (sexo == 2) & (ecivil != 1) & (edad > 24 & edad < 60) & (activ == 1) & (hijos == `i') & (index_btm == 1)

	local b_3_`i' = string(round(_b[y0101h],.001),"%9.3f")
	local alpha_3_`i' = string(round(_b[_cons],.001),"%9.3f")
	
	*#4	WBTM NOT MARRIED
	reg y_tot y0101h if (sexo == 2) & (ecivil != 1) & (edad > 24 & edad < 60) & (activ == 1) & (hijos == `i') & (index_btm == 0)

	local b_4_`i' = string(round(_b[y0101h],.001),"%9.3f")
	local alpha_4_`i' = string(round(_b[_cons],.001),"%9.3f")

	}	
	
	
*** EXCEL: parameters python ***

putexcel set "C:\Users\Patricio De Araya\Dropbox\LocalRA\LocalBTM\Stata btm\casen2015\Results\param_python.xlsx", sheet("BTM") modify

*** MARRIED ***
putexcel E7= `b_1_0', nformat(number_d2)
putexcel E6= `alpha_1_0', nformat(number_d2)
putexcel F7= `b_1_1', nformat(number_d2)
putexcel F6= `alpha_1_1', nformat(number_d2)
putexcel G7= `b_1_2', nformat(number_d2)
putexcel G6= `alpha_1_2', nformat(number_d2)
putexcel H7= `b_1_3', nformat(number_d2)
putexcel H6= `alpha_1_3', nformat(number_d2)
putexcel E9= `b_2_0', nformat(number_d2)
putexcel E8= `alpha_2_0', nformat(number_d2)
putexcel F9= `b_2_1', nformat(number_d2)
putexcel F8= `alpha_2_1', nformat(number_d2)
putexcel G9= `b_2_2', nformat(number_d2)
putexcel G8= `alpha_2_2', nformat(number_d2)
putexcel H9= `b_2_3', nformat(number_d2)
putexcel H8= `alpha_2_3', nformat(number_d2)

*** NOT MARRIED ***
putexcel E13= `b_3_0', nformat(number_d2)
putexcel E12= `alpha_3_0', nformat(number_d2)
putexcel F13= `b_3_1', nformat(number_d2)
putexcel F12= `alpha_3_1', nformat(number_d2)
putexcel G13= `b_3_2', nformat(number_d2)
putexcel G12= `alpha_3_2', nformat(number_d2)
putexcel H13= `b_3_3', nformat(number_d2)
putexcel H12= `alpha_3_3', nformat(number_d2)
putexcel E15= `b_4_0', nformat(number_d2)
putexcel E14= `alpha_4_0', nformat(number_d2)
putexcel F15= `b_4_1', nformat(number_d2)
putexcel F14= `alpha_4_1', nformat(number_d2)
putexcel G15= `b_4_2', nformat(number_d2)
putexcel G14= `alpha_4_2', nformat(number_d2)
putexcel H15= `b_4_3', nformat(number_d2)
putexcel H14= `alpha_4_3', nformat(number_d2)

