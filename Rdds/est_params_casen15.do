/*
* =========================================================
	project: BTM
	date: 16-07-2023
	objective:  Estimations using CASEN 2015
* =========================================================
*/

/*
Queremos incluir una función en el modelo de ingresos totales del hogar. Vamos a simular ingresos totales de la siguiente manera:

I_total = alpha*(earnings)^(1-\mu) + BTM (si es elegible etc), para mujeres que trabajan (H=1).     (1)
I_total = z, para mujeres que no trabajan.     (2)

alpha, mu, y z serán distintos para mujeres casadas/no casadas y con 0, 1, 2, >=3 hijos (8 sets de parámetros)

Vamos a estimar alpha, \mu y b fuera del modelo, con datos de la CASEN (luego, esos parámetros vendrán dados cuando estimamos el modelo). 

Usando CASEN 2015, hay que calcular Y_tot = ingresos totales del hogar - ingresos por BTM. Luego, por MCO, estimar:

1. log(Y_tot) = a + b*ingresos laborales + error, para mujeres (edad en rango correspondiente) que trabajan, separado por casada/no casada y número de hijos

Luego, guardar exp(a) y (1-b)  (para después meter a python) 

2. Y_tot = promedio de ingresos totales hogar para mujeres que no trabajan, (separado por casada, no casada, número de hijos). Este será nuestros parámetros z de la ecuación (2)


Por lo tanto, hay que trabajar en dos puntos

(i) modificar la función de ingresos laborales.
(ii) programar el do-file que estima alpha, \mu y z.
(iii) Bonus: Quiero ver si las estimaciones (a y b) en la regresion log(Y_total) = a + b ingresos laborales + u cambian si comparamos dos muestras: mujeres con BTM, mujeres sin BTM. La prox vez que nos juntemos, veamos estos resultados (no es necesario preparar nada muy fancy, solo verlos en stata).
*/
* ------------------------------------------------------------------------------- *
* ----------------------- GLOBALES: UBICACION DE ARCHIVOS ----------------------- *
* ------------------------------------------------------------------------------- *
global main "/Users/antoniaaguilera/Desktop/BTM-paper/"
global tables "$main/tables"
global data "$main/data"

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
use "/Users/antoniaaguilera/Desktop/BTM-paper/data/Casen 2015.dta", clear

// clean ingresos btm 
replace y25f = . if y25f == 0
tostring y25f, g(ybtm)
destring ybtm, replace 
replace ybtm = . if ybtm == 99
							
// mensualizar ingresos btm 
replace ybtm = ybtm/12 if y25fp == 2
replace ybtm = 0 if ybtm == .

// beneficiaria btm 
gen beneficiaria_btm = (ybtm != 0)

// casada 
gen casada = (ecivil == 1 | ecivil == 3)

// ingresos totales
gen y_tot_new = ytotcor - ybtm
gen log_y = log(y_tot_new)

// hijos cat 
tostring s4, g(n_hijos)
destring n_hijos, replace
replace n_hijos = 3 if n_hijos>= 3
 
* -------------------------------- *
* ---------- ESTIMACIÓN ---------- *
* -------------------------------- *

// guardar coefs  
forval casada = 0/1 {
	forval n_hijos = 0/3 {
		
		reg log_y ytrabajocor if sexo == 2 & activ ==  1 & (edad>=25 & edad<60) & casada == `casada' & n_hijos == `n_hijos', r
		local alpha_`casada'_`n_hijos' = _b[_cons]
		local beta_`casada'_`n_hijos'  = _b[ytrabajocor]

	}
}

// comparar beneficiarias vs no beneficiarias 

// no beneficiaria
reg log_y ytrabajocor if sexo == 2 & activ ==  1 &(edad>=25 & edad<60) & beneficiaria_btm == 0 ,r

outreg2 using "$tables/btm_beneficiarios_comp.tex", replace ctitle("No Beneficiarias")
outreg2 using "$tables/btm_beneficiarios_comp.doc", replace ctitle("No Beneficiarias")
	
// beneficiaria
reg log_y ytrabajocor if sexo == 2 & (edad>=25 & edad<60) & beneficiaria_btm == 1 ,r

outreg2 using "$tables/btm_beneficiarios_comp.tex", append ctitle("Beneficiarias")
outreg2 using "$tables/btm_beneficiarios_comp.doc", append ctitle("Beneficiarias")

* -------------------------------- *
* --------- GUARDAR COEFS -------- *
* -------------------------------- *

clear all 

set obs 4

//n_hijos 
gen n_hijos = _n-1
expand 2
//casada 
gen casada = 0 if _n<=4
replace casada = 1 if _n>4

// guardar 
gen alpha = . 
gen beta  = .
forval casada = 0/1 {
	forval n_hijos=0/3 {
		replace alpha = `alpha_`casada'_`n_hijos'' if casada == `casada' & n_hijos == `n_hijos'
		replace beta = `beta_`casada'_`n_hijos'' if casada == `casada' & n_hijos == `n_hijos'
	}
}
// vars 
gen exp_alpha = exp(alpha)
gen one_minus_beta = 1-beta

export excel "$data/estimation_casen15.xlsx", first(var) replace 
