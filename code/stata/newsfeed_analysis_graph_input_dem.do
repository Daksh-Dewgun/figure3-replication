* Extract p-values for Figure 3

clear all

use $newsfeed_data

keep if partisanship_w1 == 2

eststo clear

* Create a temporary file to store p-values
tempname p_values_file
tempfile p_values_filepath
file open `p_values_file' using `p_values_filepath', write replace
file write `p_values_file' "regression_name,p_value" _n

* Engagement

ppmlhdfe Numberoflikes TabSource_num, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local z = `b_tab'/`se_tab'
local pval = 2*(1-normal(abs(`z')))
file write `p_values_file' "Numberoflikes,`pval',`b_tab'" _n

ppmlhdfe Numberofretweets TabSource_num, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local z = `b_tab'/`se_tab'
local pval = 2*(1-normal(abs(`z')))
file write `p_values_file' "Numberofretweets,`pval',`b_tab'" _n

ppmlhdfe Numberofcomments TabSource_num, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local z = `b_tab'/`se_tab'
local pval = 2*(1-normal(abs(`z')))
file write `p_values_file' "Numberofcomments,`pval',`b_tab'" _n

* Political content

reghdfe partisan TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "partisan,`pval',`b_tab'" _n

reghdfe conservative TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "conservative,`pval',`b_tab'" _n

reghdfe liberal TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "liberal,`pval',`b_tab'" _n

reghdfe conservative TabSource_num $controls if partisan == 1, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "cons_over_partisan,`pval',`b_tab'" _n

* Political activists

reghdfe pol_activ_acc TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "pol_activ_acc,`pval',`b_tab'" _n

reghdfe cons_polit_activ TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "cons_polit_activ,`pval',`b_tab'" _n

reghdfe lib_polit_activ TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "lib_polit_activ,`pval',`b_tab'" _n

reghdfe cons_polit_activ TabSource_num $controls if pol_activ_acc == 1, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "cons_polit_activ_over_p,`pval',`b_tab'" _n

* News outlets

reghdfe news_acc TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "news_acc,`pval',`b_tab'" _n

reghdfe cons_news TabSource_num $controls, absorb(id wave) cluster(id) 
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "cons_news,`pval',`b_tab'" _n

reghdfe lib_news TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "lib_news,`pval',`b_tab'" _n

reghdfe cons_news TabSource_num $controls, absorb(id wave) cluster(id) 
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "cons_news,`pval',`b_tab'" _n

* O

reghdfe entertainment_acc TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "entertainment_acc,`pval',`b_tab'" _n

reghdfe official_acc TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "official_acc,`pval',`b_tab'" _n

reghdfe other_acc TabSource_num $controls, absorb(id wave) cluster(id)
local b_tab = _b[TabSource_num]
local se_tab = _se[TabSource_num]
local df = e(df_r)
local t = `b_tab'/`se_tab'
local pval = 2*ttail(`df', abs(`t'))
file write `p_values_file' "other_acc,`pval',`b_tab'" _n

* Close the file and save
file close `p_values_file'
preserve
insheet using `p_values_filepath', clear comma
export delimited using "../../regression_outputs/newsfeed_regression_p_values_dem.csv", replace
restore
