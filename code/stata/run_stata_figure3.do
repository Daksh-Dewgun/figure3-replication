/*------------------------------------------------------------------------------
  run_stata_figure3.do
  Runs the full Stata pipeline needed to produce Figure 3.
  Steps:
    1. newsfeed_content_shares.do  - collapse raw data
    2. newsfeed_analysis_graph_input.do     - main p-values CSV
    3. newsfeed_analysis_graph_input_rep.do - Republicans/Independents
    4. newsfeed_analysis_graph_input_dem.do - Democrats
------------------------------------------------------------------------------*/

* Set working directory to the stata folder
cd "`c(pwd)'"

* Define globals
global newsfeed_data "../../data/main_data_and_newsfeed_data.dta"
global controls "gender age educ_d race_d tw_often_w1 tw_often_tweet_w1 use_tw_read_pol_w1 use_tw_pol_activ_w1 use_tw_read_nonpol_w1 use_tw_entertain_w1 use_tw_connect_w1 use_tw_prof_w1 use_tw_other_w1 i.partisanship_w1"

* Step 1: Collapse newsfeed data
do newsfeed_content_shares.do

* Step 2: Run regressions and export p-values
do newsfeed_analysis_graph_input.do
do newsfeed_analysis_graph_input_rep.do
do newsfeed_analysis_graph_input_dem.do

di "Stata pipeline complete."
