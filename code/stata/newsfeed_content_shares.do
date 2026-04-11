clear all

use $newsfeed_data

do "./Prerequisites/regressions.do" 

gen n = 1

drop if treat_algo == 1 & TabSource == "Chrono" & wave == 1
drop if treat_algo == 0 & TabSource == "Algorithm" & wave == 1
drop if treat_algo == 1 & TabSource == "Chrono" & wave == 2
drop if treat_algo == 0 & TabSource == "Algorithm" & wave == 2

collapse (mean) switch pre_algo treat_algo switch_* age gender educ race educ_d race_d /// user-level vars
               tw_often_w1 partisanship_w1 strength_partisanship_w1 delta_thermo_w1 ///
			   ladder_w1 all_things_w1 actual_switch_algo actual_switch_rco use_tw_read_pol_w1 ///
			   use_tw_pol_activ_w1 use_tw_read_nonpol_w1 use_tw_entertain_w1 use_tw_connect_w1 use_tw_prof_w1 use_tw_other_w1 tw_often_tweet_w1 deviceused_w1 /// more w1
               partisanship_w2 strength_partisanship_w2 thermo_dem_w2 thermo_rep_w2 ladder_w2 all_things_w2 /// w2 vars  
               use_tw_read_pol_w2 use_tw_pol_activ_w2 use_tw_read_nonpol_w2 use_tw_entertain_w2 use_tw_connect_w2 ///
			   use_tw_prof_w2 use_tw_other_w2 tw_often_w2 tw_often_tweet_w2 /// more w2
			   entertainment_acc official_acc cons_polit_activ cons_news lib_polit_activ lib_news other_acc ///
               mention_news political_topics entertainment_topics /// content proportions
               account_ideological_score news_outlet_ideological_score /// avg ideology exposure
               conservative liberal news_acc pol_activ_acc /// account type proportions
         (sum) Numberoflikes Numberofretweets Numberofcomments /// engagement totals
         (count) n /// number of posts per user-wave
         , by(id wave)

rename n post_cout

reshape wide mention_news political_topics entertainment_topics ///
            account_ideological_score news_outlet_ideological_score ///
            conservative liberal news_acc pol_activ_acc entertainment_acc ///
			official_acc cons_polit_activ cons_news lib_polit_activ lib_news other_acc ///
            Numberoflikes Numberofretweets Numberofcomments ///
            post_cout, i(id) j(wave)
			
* Standardize the account type proportion variables (all have "2" suffix after reshape)
foreach var of varlist conservative2 liberal2 news_acc2 pol_activ_acc2 entertainment_acc2 ///
                      official_acc2 cons_polit_activ2 cons_news2 lib_polit_activ2 lib_news2 other_acc2 {
    egen `var'_std = std(`var')
}

save "../../../data/newsfeed_data_collapsed.dta", replace