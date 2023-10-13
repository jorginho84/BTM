

// fig 4: check
do "$dofiles/covariates_balance.do"

// fig 5: check
do "$dofiles/static.do"

// tabla 4 a grafico: check
do "$dofiles/bws.do"

// tabla 3 nuevo formato, mean pfse: check
do "$dofiles/static_meanpfse.do"

// tabla 3 nuevo formato, min pfse 
do "$dofiles/static_minpfse.do"

// grafico de efectos dinámicos mean_pfse
do "$dofiles/plot_meanpfse.do"

// grafico de efectos dinámicos min_pfse
do "$dofiles/plot_minpfse.do"
