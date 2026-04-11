program regression_table

args y table_name additonal_controls add_twitteruse_w2

if "`additonal_controls'" == ""{
	global extra_controls 
} 
else {
	global extra_controls $`additonal_controls'
}

global controls_demo gender age educ_d race_d 
global controls_twuse tw_often_w1 tw_often_tweet_w1 use_tw_*_w1  
global controls_polit i.partisanship_w1
global controls_all $extra_controls $controls_demo $controls_polit $controls_twuse

* Regressions

* Baseline ITT on the full sample (1)

qui reg `y' treat_algo $extra_controls, robust
estimates store c1
qui sum `e(depvar)' if e(sample)
estadd scalar Mean= r(mean)

* ITT split based on previous newsfeed setting (2)

qui reg `y' switch_to_algo switch_to_rco pre_algo $extra_controls, robust
estimates store c2
qui sum `e(depvar)' if e(sample)
estadd scalar Mean= r(mean)
test _b[switch_to_algo] + _b[switch_to_rco] = 0
estadd scalar p_value = r(p)
test _b[switch_to_algo] = _b[pre_algo]
estadd scalar p_value_2 = r(p)

* ITT split based on previous newsfeed setting (3)
* Controlling for:
* - Demographic controls
* - Twitter use pre-treatment levels
* - Political affiliation

qui reg `y' switch_to_algo switch_to_rco pre_algo $controls_all, robust
estimates store c3
qui sum `e(depvar)' if e(sample)
estadd scalar Mean= r(mean)
test _b[switch_to_algo] + _b[switch_to_rco] = 0
estadd scalar p_value = r(p)
test _b[switch_to_algo] = _b[pre_algo]
estadd scalar p_value_2 = r(p)

* ITT split based on previous newsfeed setting (4)
* Controlling for:
* - Demographic controls
* - Twitter use pre-treatment levels
* - Political affiliation
* - Twitter use post-treatment levels

if "`add_twitteruse_w2'" == ""{
	qui reg `y' switch_to_algo switch_to_rco pre_algo i.tw_often_w2 $controls_all, robust
	estimates store c4
	qui sum `e(depvar)' if e(sample)
	estadd scalar Mean= r(mean)
	test _b[switch_to_algo] + _b[switch_to_rco] = 0
	estadd scalar p_value = r(p) 
	test _b[switch_to_algo] = _b[pre_algo]
	estadd scalar p_value_2 = r(p)
}

* ITT split based on previous newsfeed setting (5)
* Controlling for:
* - demographic controls
* - Twitter use pre-treatment levels
* - Political affiliation
* - Predicted previous setting

qui reg `y' switch_to_algo switch_to_rco pre_algo prev_hat $controls_all, robust
estimates store c5
qui sum `e(depvar)' if e(sample)
estadd scalar Mean= r(mean)
test _b[switch_to_algo] + _b[switch_to_rco] = 0
estadd scalar p_value = r(p)
test _b[switch_to_algo] = _b[pre_algo]
estadd scalar p_value_2 = r(p)

* LATE from IV with split based on previous newsfeed setting (6)
* Similar to column (2)
* No controls

preserve
rename switch_to_algo switch_to_algo_itt
rename switch_to_rco switch_to_rco_itt
rename actual_switch_algo switch_to_algo
rename actual_switch_rco switch_to_rco

qui ivreg2 `y' (switch_to_algo switch_to_rco = switch_to_algo_itt switch_to_rco_itt) pre_algo $extra_controls, robust
estimates store c6
qui sum `e(depvar)' if e(sample)
estadd scalar Mean= r(mean)
test _b[switch_to_algo] + _b[switch_to_rco] = 0
estadd scalar p_value = r(p)
test _b[switch_to_algo] = _b[pre_algo]
estadd scalar p_value_2 = r(p)

* LATE from IV with split based on previous newsfeed setting (7)
* Similar to column (3)
* Controlling for:
* - Demographic controls
* - Twitter use pre-treatment levels
* - Political affiliation

qui ivreg2 `y' (switch_to_algo switch_to_rco = switch_to_algo_itt switch_to_rco_itt) pre_algo $controls_all, robust
estimates store c7
qui sum `e(depvar)' if e(sample)
estadd scalar Mean= r(mean)
test _b[switch_to_algo] + _b[switch_to_rco] = 0
estadd scalar p_value = r(p)
test _b[switch_to_algo] = _b[pre_algo]
estadd scalar p_value_2 = r(p)
restore

estout c* using `table_name',  ///
		keep(treat_algo switch_to_algo switch_to_rco pre_algo prev_hat)  ///
		order(treat_algo switch_to_algo switch_to_rco pre_algo)  ///
		varlabels(treat_algo "Treatment Algo"  /// 
		switch_to_algo "$\beta_1$: Initial Chrono $\times$ Treatment Algo" ///
		switch_to_rco "$\beta_2$: Initial Algo $\times$ Treatment Chrono" /// 
		pre_algo "$\beta_3$: Initial Algo" /// 
		prev_hat "Predicted Initial Algo") ///
		cells(b(star fmt(3)) se(par fmt(3))) starlevels(* 0.10 ** 0.05 *** 0.01) ///
		stats(Mean p_value p_value_2 N, fmt(%9.2f %9.2f %9.2f %9.0f) ///
		labels("\midrule Mean dependent variable" "P-value $\beta_1=-\beta_2$" "P-value $\beta_1=\beta_3$" "Observations")) ///
		collabels(none) ///
		mlabels(none) ///
		style(tex) replace

estout c*, keep(treat_algo switch_to_algo switch_to_rco pre_algo prev_hat) order(treat_algo switch_to_algo switch_to_rco pre_algo) varlabels(treat_algo "TreatAlgo" switch_to_algo "$\beta_1$: TreatAlgo x (1-PreAlgo)" switch_to_rco "$\beta_2$: (1-TreatAlgo) x PreAlgo" pre_algo "PreAlgo" prev_hat "Pred(Previous Setting)") cells(b(star fmt(3)) se(par fmt(3))) starlevels(* 0.10 ** 0.05 *** 0.01) stats(Mean p_value p_value_2 N, fmt(%9.2f %9.2f %9.2f %9.0f) labels("Mean dependent variable" "P-value $\beta_1=-\beta_2$" "P-value $\beta_1=\beta_3$" "Observations")) replace

estimates clear

end
