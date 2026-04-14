# Housekeeping
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import os
from matplotlib.legend_handler import HandlerTuple

# Font used throughout all plot text
font_used = 'Arial'

# Global display flags:
# PLOT_X_AXIS controls whether x-axis ticks and spine are shown
# X_LABEL_ON_TOP places the x-axis label above the chart rather than below
PLOT_X_AXIS = True
X_LABEL_ON_TOP = True


def create_plot(df, p_values_csv, output_filename, plot_title_suffix=''):
    """
    Generate a multi-panel horizontal bar chart comparing content seen in
    chronological vs. algorithmic Twitter/X newsfeeds.

    Parameters
    ----------
    df               : DataFrame containing newsfeed observations, with a
                       'TabSource' column that is either 'Chrono' or 'Algorithm'.
    p_values_csv     : Path to a CSV file with regression results (p-values and
                       coefficients) used to annotate each bar pair.
    output_filename  : Filename (PDF) to save the finished figure into the
                       project's 'figs' directory.
    plot_title_suffix: Optional string appended to console messages (not shown
                       on the figure itself).
    """

    # ------------------------------------------------------------------ #
    # 1. Load regression results (p-values + coefficients)
    # ------------------------------------------------------------------ #
    p_values_df = pd.read_csv(p_values_csv)

    # Build a dict: {regression_name -> p_value}
    p_values_dict = dict(zip(p_values_df['regression_name'], p_values_df['p_value']))

    # Build a dict: {regression_name -> coefficient}
    # The coefficient column may be named 'coefficient' or 'v3' depending on
    # which regression output file was produced.
    if 'coefficient' in p_values_df.columns:
        coef_dict = dict(zip(p_values_df['regression_name'], p_values_df['coefficient']))
    elif 'v3' in p_values_df.columns:
        coef_dict = dict(zip(p_values_df['regression_name'], p_values_df['v3']))
    else:
        coef_dict = {}

    # ------------------------------------------------------------------ #
    # 2. Helper functions for formatting annotation text
    # ------------------------------------------------------------------ #

    def format_p_value(p_value):
        """Return a human-readable p-value string (e.g. 'p < 0.001')."""
        try:
            p_float = float(p_value)
            if p_float < 0.001:
                return "p < 0.001"
            else:
                return f"p = {p_float:.3f}"
        except:
            return ""

    def format_coef_and_pval(coef, p_value, is_engagement=False):
        """
        Return a combined coefficient + p-value annotation string.

        For engagement metrics (likes, retweets, comments) the coefficient is
        an OLS log-scale estimate, so we exponentiate and multiply by 100 to
        express it as a percentage-point change in the raw count.
        For all other (proportion) outcomes the coefficient is shown directly.
        """
        try:
            coef_float = float(coef)
            if is_engagement:
                # Convert log coefficient to a percentage-point effect
                coef_float = np.exp(coef_float) * 100
                coef_str = f"{int(round(coef_float))}"
            else:
                coef_str = f"{coef_float:.3f}"
            p_float = float(p_value)
            if p_float < 0.001:
                return f"{coef_str}, p < 0.001"
            else:
                return f"{coef_str}, p = {p_float:.3f}"
        except:
            return ""

    # Pre-compute formatted p-value strings for every regression term
    formatted_p_values = {k: format_p_value(v) for k, v in p_values_dict.items()}

    # Engagement variables receive the exponentiated-coefficient treatment
    engagement_vars_list = ['Numberoflikes', 'Numberofretweets', 'Numberofcomments']
    formatted_coef_pval = {}
    for k in p_values_dict.keys():
        is_engagement = k in engagement_vars_list
        formatted_coef_pval[k] = format_coef_and_pval(
            coef_dict.get(k, ''), p_values_dict.get(k, ''), is_engagement
        )

    # ------------------------------------------------------------------ #
    # 3. Human-readable labels for variable names shown on the y-axis
    # ------------------------------------------------------------------ #
    label_mapping = {
        'Numberoflikes': 'Likes',
        'Numberofretweets': 'Reposts',
        'Numberofcomments': 'Comments',
        'partisan': 'Any political content',
        'conservative': 'Conservative content',
        'liberal': 'Liberal content',
        'share_conservative_content': 'Conservative among political',
        'news_acc': 'Any news',
        'official_acc': 'Official accounts',
        'other_acc': 'Other accounts',
        'entertainment_acc': 'Entertainment',
        'pol_activ_acc': 'Any political activist',
        'cons_polit_activ': 'Conservative activist',
        'cons_news': 'Conservative news',
        'lib_polit_activ': 'Liberal activist',
        'lib_news': 'Liberal news',
        'share_conservative_activist': 'Conservative among activists',
        'share_conservative_news': 'Conservative among news'
    }

    def get_label(var):
        """Look up the display label for a variable name."""
        return label_mapping.get(var, var)

    def get_coef_pval(var):
        """
        Return the pre-formatted coefficient + p-value string for a variable.

        Some 'share_conservative_*' variables are stored under different keys
        in the regression output, so we remap them here before looking up.
        """
        lookup_var = var
        if var == 'share_conservative_content':
            lookup_var = 'cons_over_partisan'
        elif var == 'share_conservative_activist':
            lookup_var = 'cons_polit_activ_over_p'
        elif var == 'share_conservative_news':
            lookup_var = 'cons_news_over_p'
        return formatted_coef_pval.get(lookup_var, "")

    # ------------------------------------------------------------------ #
    # 4. Compute per-variable means and 95 % confidence intervals
    # ------------------------------------------------------------------ #

    def calc_means_with_ci(df, vars, confidence=0.95):
        """
        For each variable in `vars`, compute the mean and a t-based confidence
        interval separately for the Chrono and Algorithm sub-samples.

        'share_conservative_content' is a derived variable (proportion of
        political posts that are conservative) and is handled as a special case:
        we first filter to only politically-tagged rows before computing the mean.

        Returns a DataFrame with one row per variable (in reversed order so that
        the first variable in the list appears at the top of the chart).
        """
        results = {
            'Chrono': [], 'Algorithm': [],
            'Chrono_CI_low': [], 'Chrono_CI_high': [],
            'Algorithm_CI_low': [], 'Algorithm_CI_high': [],
            'coef_pval': [], 'orig_vars': []
        }

        # Split the data by feed type
        chrono_df = df[df['TabSource'] == 'Chrono']
        algo_df   = df[df['TabSource'] == 'Algorithm']

        for var in vars:
            if var == 'share_conservative_content':
                # Special case: compute the share of conservative posts among
                # all partisan (political) posts in each feed condition.
                try:
                    chrono_partisan = chrono_df[chrono_df['partisan'] == 1]
                    algo_partisan   = algo_df[algo_df['partisan'] == 1]

                    if len(chrono_partisan) > 0:
                        chrono_mean = chrono_partisan['conservative'].mean()
                        chrono_sem  = stats.sem(chrono_partisan['conservative'].dropna())
                        chrono_ci   = stats.t.interval(
                            confidence,
                            len(chrono_partisan['conservative'].dropna()) - 1,
                            loc=chrono_mean, scale=chrono_sem
                        )
                    else:
                        chrono_mean = 0
                        chrono_ci   = (0, 0)

                    if len(algo_partisan) > 0:
                        algo_mean = algo_partisan['conservative'].mean()
                        algo_sem  = stats.sem(algo_partisan['conservative'].dropna())
                        algo_ci   = stats.t.interval(
                            confidence,
                            len(algo_partisan['conservative'].dropna()) - 1,
                            loc=algo_mean, scale=algo_sem
                        )
                    else:
                        algo_mean = 0
                        algo_ci   = (0, 0)

                    results['Chrono'].append(chrono_mean)
                    results['Chrono_CI_low'].append(chrono_ci[0])
                    results['Chrono_CI_high'].append(chrono_ci[1])
                    results['Algorithm'].append(algo_mean)
                    results['Algorithm_CI_low'].append(algo_ci[0])
                    results['Algorithm_CI_high'].append(algo_ci[1])
                    results['orig_vars'].append(var)
                    results['coef_pval'].append(get_coef_pval(var))
                except:
                    continue

            elif var not in df.columns:
                # Skip variables that are absent from this dataset
                continue

            else:
                # Standard case: compute mean + CI directly from the column
                try:
                    chrono_mean = chrono_df[var].mean()
                    results['Chrono'].append(chrono_mean)

                    chrono_sem = stats.sem(chrono_df[var].dropna())
                    chrono_ci  = stats.t.interval(
                        confidence,
                        len(chrono_df[var].dropna()) - 1,
                        loc=chrono_mean, scale=chrono_sem
                    )
                    results['Chrono_CI_low'].append(chrono_ci[0])
                    results['Chrono_CI_high'].append(chrono_ci[1])

                    algo_mean = algo_df[var].mean()
                    results['Algorithm'].append(algo_mean)

                    algo_sem = stats.sem(algo_df[var].dropna())
                    algo_ci  = stats.t.interval(
                        confidence,
                        len(algo_df[var].dropna()) - 1,
                        loc=algo_mean, scale=algo_sem
                    )
                    results['Algorithm_CI_low'].append(algo_ci[0])
                    results['Algorithm_CI_high'].append(algo_ci[1])

                    results['orig_vars'].append(var)
                    results['coef_pval'].append(get_coef_pval(var))
                except:
                    continue

        # Return an empty DataFrame with the expected columns if no data
        if not results['Chrono']:
            return pd.DataFrame(columns=[
                'Chrono', 'Algorithm', 'Chrono_CI_low', 'Chrono_CI_high',
                'Algorithm_CI_low', 'Algorithm_CI_high', 'coef_pval', 'orig_vars', 'index'
            ])

        means = pd.DataFrame(results)
        # Replace raw variable names with human-readable labels
        means['index'] = [get_label(var) for var in results['orig_vars']]
        # Reverse row order so the first variable in the input list renders at
        # the top of the horizontal bar chart
        means = means.iloc[::-1].reset_index(drop=True)
        return means

    # ------------------------------------------------------------------ #
    # 5. Set up the figure: 5 panels with heights proportional to bar count
    # ------------------------------------------------------------------ #

    # Number of variables (bars) in each panel
    num_bars    = [3, 4, 3, 3, 3]
    total_bars  = sum(num_bars)
    fig_height  = 16

    # Each sub-plot's height is proportional to its share of the total bars
    heights = [n * fig_height / total_bars for n in num_bars]
    fig, axs = plt.subplots(
        5, 1, figsize=(16, fig_height),
        gridspec_kw={'height_ratios': heights}
    )

    # Colour palette: grey for Chrono, dark red for Algorithm
    colors = ['#BCBCBC', '#B22222']

    # ------------------------------------------------------------------ #
    # 6. Core plotting function: draw a paired horizontal bar chart
    # ------------------------------------------------------------------ #

    def plot_bars(ax, data, title):
        """
        Draw paired horizontal bars for a single panel.

        For each variable there are two bars stacked vertically:
          - lower bar: Chrono feed (grey)
          - upper bar: Algorithm feed (dark red)
        Error bars show the 95 % confidence interval.
        Numeric value labels are placed to the right of each bar.
        The regression Δ and p-value annotation is shown below the variable label.
        """
        if data.empty:
            return

        bar_height = 0.4   # height of each individual bar
        y_offset   = 0.41  # vertical separation between the two bars in a pair

        try:
            y_pos = np.arange(len(data))   # integer y-positions for each variable

            # -- Draw filled bars (Chrono below, Algorithm above) ----------
            ax.barh(y_pos - y_offset/2, data['Chrono'],    height=bar_height,
                    color=colors[0], label='Chrono',    linewidth=0)
            # Thin edge drawn separately (almost invisible, linewidth=0.01) to
            # allow the legend handler to render a matching outline swatch
            ax.barh(y_pos - y_offset/2, data['Chrono'],    height=bar_height,
                    facecolor='none', edgecolor=colors[0], linewidth=0.01)

            ax.barh(y_pos + y_offset/2, data['Algorithm'], height=bar_height,
                    color=colors[1], label='Algorithm', linewidth=0)
            ax.barh(y_pos + y_offset/2, data['Algorithm'], height=bar_height,
                    facecolor='none', edgecolor=colors[1], linewidth=0.01)

            # -- Confidence interval error bars ----------------------------
            # xerr expects [lower_errors, upper_errors] where each is the
            # distance from the mean to the CI bound (not the absolute value).
            error_chrono = [
                data['Chrono'] - data['Chrono_CI_low'],
                data['Chrono_CI_high'] - data['Chrono']
            ]
            ax.errorbar(data['Chrono'], y_pos - y_offset/2,
                        xerr=error_chrono, fmt='none', ecolor='black', capsize=5)

            error_algo = [
                data['Algorithm'] - data['Algorithm_CI_low'],
                data['Algorithm_CI_high'] - data['Algorithm']
            ]
            ax.errorbar(data['Algorithm'], y_pos + y_offset/2,
                        xerr=error_algo, fmt='none', ecolor='black', capsize=5)

            # -- Axis spine styling ----------------------------------------
            # Keep only the bottom spine (and optionally hide that too)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(PLOT_X_AXIS)
            ax.spines['left'].set_visible(False)

            # -- Panel title (bold, positioned above the plot area) --------
            x_offset = -0.61  # fraction of axes width to the left of the origin
            ax.text(x_offset, 1.15, title,
                    transform=ax.transAxes,
                    fontsize=int(0.95 * 27),
                    fontname=font_used,
                    fontweight='bold',
                    horizontalalignment='left',
                    verticalalignment='bottom')

            # -- X-axis label (above or below depending on global flag) ----
            xlabel_text = ('Average Number'
                           if title == 'Engagement'
                           else 'Probability of Seeing a Post')
            xlabel_fontsize = int(0.95 * 19)

            if X_LABEL_ON_TOP:
                # Render as a text annotation above the chart area
                ax.text(0.5, 1.05, xlabel_text,
                        transform=ax.transAxes,
                        fontsize=xlabel_fontsize,
                        fontname=font_used,
                        horizontalalignment='center',
                        verticalalignment='bottom')
            else:
                ax.set_xlabel(xlabel_text, fontsize=xlabel_fontsize, fontname=font_used)

            ax.tick_params(axis='y', labelsize=int(0.95 * 23))

            # -- X-axis tick formatting ------------------------------------
            if PLOT_X_AXIS:
                if title == 'Engagement':
                    # Show large integer counts with thousands separators
                    ax.xaxis.set_major_formatter(
                        plt.FuncFormatter(lambda x, p: f'{int(x):,}')
                    )
                else:
                    # Show proportions to two decimal places
                    ax.xaxis.set_major_formatter(
                        plt.FuncFormatter(lambda x, p: f'{x:.2f}')
                    )
                for label in ax.get_xticklabels():
                    label.set_fontname(font_used)
                    label.set_fontsize(int(0.95 * 16))
            else:
                # Hide all x-axis tick labels and ticks
                ax.set_xticklabels([])
                ax.tick_params(axis='x', which='both', length=0)

            # -- Y-axis: hide default tick labels; draw custom text instead -
            ax.set_yticks(y_pos)
            ax.set_yticklabels([])

            # Place variable label and Δ annotation to the left of each pair
            for i, (pos, label, coef_pval) in enumerate(
                    zip(y_pos, data['index'], data['coef_pval'])):

                # The label is aligned with the Algorithm (upper) bar
                label_pos = pos + y_offset / 2
                ax.text(-0.01, label_pos, label,
                        transform=ax.get_yaxis_transform(),
                        fontsize=int(0.95 * 23),
                        fontname=font_used,
                        horizontalalignment='right',
                        verticalalignment='center')

                # If a regression annotation is available, draw it below the
                # variable label (aligned with the Chrono / lower bar)
                if coef_pval:
                    vertical_offset = 0.45  # shift downward from label_pos

                    if title == 'Engagement':
                        # Prefix with Δ = and append % for engagement counts
                        parts = coef_pval.split(',')
                        coef_pval_with_delta = (
                            '$\\Delta$ = ' + parts[0] + '%,' + parts[1]
                            if len(parts) > 1
                            else '$\\Delta$ = ' + coef_pval + '%'
                        )
                    else:
                        coef_pval_with_delta = '$\\Delta$ = ' + coef_pval

                    ax.text(-0.01, label_pos - vertical_offset,
                            coef_pval_with_delta,
                            transform=ax.get_yaxis_transform(),
                            fontsize=int(0.95 * 18),
                            fontname=font_used,
                            horizontalalignment='right',
                            verticalalignment='center')

            # -- X-axis limits and numeric value labels --------------------

            if title != 'Engagement':
                # Fix proportion panels to [0, 0.6] for comparability
                ax.set_xlim(0.00, 0.6)

            if title == 'Engagement':
                # For engagement, auto-size x-limit with generous padding so
                # the numeric value labels (e.g. '1,234') fit inside the figure
                max_ci_width = max(
                    max(data['Chrono_CI_high']    - data['Chrono']),
                    max(data['Algorithm_CI_high'] - data['Algorithm'])
                )
                padding_factor = 0.15
                max_value = max(
                    data['Chrono_CI_high'].max(),
                    data['Algorithm_CI_high'].max()
                )
                ax.set_xlim(0, max_value * 1.4)
                extra_space = max_ci_width * 1.5

                # Draw numeric labels to the right of each error bar
                for i, (chrono_v, algo_v) in enumerate(
                        zip(data['Chrono'], data['Algorithm'])):
                    chrono_ci_width = data['Chrono_CI_high'].iloc[i] - chrono_v
                    algo_ci_width   = data['Algorithm_CI_high'].iloc[i] - algo_v
                    small_padding   = max_ci_width * padding_factor

                    ax.text(chrono_v + chrono_ci_width + small_padding + extra_space,
                            y_pos[i] - y_offset / 2,
                            f'{int(chrono_v)}', va='center',
                            fontsize=int(0.95 * 18), fontname=font_used)
                    ax.text(algo_v + algo_ci_width + small_padding + extra_space,
                            y_pos[i] + y_offset / 2,
                            f'{int(algo_v)}', va='center',
                            fontsize=int(0.95 * 18), fontname=font_used)

            else:
                # Proportion panels: calculate label placement relative to
                # the widest CI so every label clears the error bar
                max_ci_width = max(
                    max(data['Chrono_CI_high']    - data['Chrono']),
                    max(data['Algorithm_CI_high'] - data['Algorithm'])
                )
                padding    = max_ci_width * 0.8
                extra_space = max_ci_width * 2

                for i, (chrono_v, algo_v) in enumerate(
                        zip(data['Chrono'], data['Algorithm'])):
                    chrono_ci_width = data['Chrono_CI_high'].iloc[i] - chrono_v
                    algo_ci_width   = data['Algorithm_CI_high'].iloc[i] - algo_v

                    ax.text(chrono_v + chrono_ci_width + padding + extra_space,
                            y_pos[i] - y_offset / 2,
                            f'{chrono_v:.3f}', va='center',
                            fontsize=int(0.95 * 18), fontname=font_used)
                    ax.text(algo_v + algo_ci_width + padding + extra_space,
                            y_pos[i] + y_offset / 2,
                            f'{algo_v:.3f}', va='center',
                            fontsize=int(0.95 * 18), fontname=font_used)

        except Exception as e:
            print(f"Error in plot_bars: {str(e)}")

    # ------------------------------------------------------------------ #
    # 7. Populate each panel with the relevant variable groups
    # ------------------------------------------------------------------ #

    # Panel 0 – Engagement metrics (likes, retweets, comments)
    engagement_vars = ['Numberoflikes', 'Numberofretweets', 'Numberofcomments']
    engagement_data = calc_means_with_ci(df, engagement_vars)
    plot_bars(axs[0], engagement_data, 'Engagement')

    # Panel 1 – Political content exposure
    political_vars = ['partisan', 'conservative', 'liberal', 'share_conservative_content']
    political_data = calc_means_with_ci(df, political_vars)
    plot_bars(axs[1], political_data, 'Political Content')
    axs[1].set_xlim(0.00, 0.6)

    # Panel 2 – Political activist accounts
    # Start with the overall activist variable; add partisan breakdowns if present
    activist_vars = ['pol_activ_acc']
    potential_activist_vars = ['cons_polit_activ', 'lib_polit_activ']
    for var in potential_activist_vars:
        if var in df.columns:
            activist_vars.append(var)
    activist_data = calc_means_with_ci(df, activist_vars)
    if not activist_data.empty:
        plot_bars(axs[2], activist_data, 'Political Activists')
        axs[2].set_xlim(0.00, 0.6)

    # Panel 3 – News outlet accounts
    news_vars = ['news_acc']
    potential_news_vars = ['cons_news', 'lib_news']
    for var in potential_news_vars:
        if var in df.columns:
            news_vars.append(var)
    news_data = calc_means_with_ci(df, news_vars)
    if not news_data.empty:
        plot_bars(axs[3], news_data, 'News Outlets')
        axs[3].set_xlim(0.00, 0.6)

    # Panel 4 – Entertainment, official, and other account types
    other_vars = ['entertainment_acc', 'official_acc', 'other_acc']
    other_data = calc_means_with_ci(df, other_vars)
    plot_bars(axs[4], other_data, 'Entertainment; Official; Other')
    axs[4].set_xlim(0.00, 0.6)

    # ------------------------------------------------------------------ #
    # 8. Global figure styling and layout
    # ------------------------------------------------------------------ #

    plt.tight_layout()

    # Override default font sizes for all plot elements
    plt.rcParams['font.size']        = int(0.95 * 36)
    plt.rcParams['axes.titlesize']   = int(0.95 * 36)
    plt.rcParams['axes.labelsize']   = int(0.95 * 36)
    plt.rcParams['xtick.labelsize']  = int(0.95 * 36)
    plt.rcParams['ytick.labelsize']  = int(0.95 * 36)

    # Adjust spacing: left margin is wide to accommodate y-axis text labels;
    # right margin leaves room for numeric value labels beside each bar
    plt.subplots_adjust(hspace=0.6, top=0.95, bottom=0.05, left=0.35, right=0.8)

    plt.rcParams['font.family'] = font_used

    # Additional bottom margin for the legend below the figure
    plt.subplots_adjust(bottom=0.08)

    # Ensure the output directory exists
    plot_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../', 'figs')
    os.makedirs(plot_folder, exist_ok=True)

    # ------------------------------------------------------------------ #
    # 9. Build the figure legend
    # ------------------------------------------------------------------ #

    handles, labels = axs[0].get_legend_handles_labels()

    class HandlerTupleOverlay(HandlerTuple):
        """
        Custom legend handler that renders each entry as two overlapping
        rectangles: a filled patch (solid colour) and an outlined patch
        (transparent fill, coloured border).  This mirrors how bars and their
        edges are drawn, giving the legend a visually consistent look.
        """
        def create_artists(self, legend, orig_handle, xdescent, ydescent,
                           width, height, fontsize, trans):
            artists = []
            for handle in orig_handle:
                patch = plt.Rectangle(
                    (xdescent, ydescent), width, height,
                    facecolor=handle.get_facecolor(),
                    edgecolor=handle.get_edgecolor(),
                    alpha=handle._alpha,
                    linewidth=handle.get_linewidth(),
                    transform=trans
                )
                artists.append(patch)
            return artists

    # Build (filled_rect, outlined_rect) tuples for Algorithm then Chrono
    # (colours are reversed so Algorithm / dark red appears first in the legend)
    legend_handles = []
    for i, color in enumerate([colors[1], colors[0]]):
        fill = plt.Rectangle((0, 0), 1, 1, facecolor=color, alpha=1.0, edgecolor='none')
        edge = plt.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor=color, linewidth=3)
        legend_handles.append((fill, edge))

    fig.legend(
        legend_handles,
        ['Content of algorithmic feed', 'Content of chronological feed'],
        handler_map={tuple: HandlerTupleOverlay()},
        loc='lower center',
        bbox_to_anchor=(0.5, -0.05),
        ncol=2,
        fontsize=int(0.95 * 21)
    )

    # Final bottom adjustment after adding the legend
    plt.subplots_adjust(bottom=0.03)

    # ------------------------------------------------------------------ #
    # 10. Save the figure
    # ------------------------------------------------------------------ #
    plot_path = os.path.join(plot_folder, output_filename)
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"Plot saved to: {plot_path}")
    plt.close()


# ------------------------------------------------------------------ #
# Entry point: generate three versions of the figure
#   1. All participants (Figure 3)
#   2. Republicans and Independents only
#   3. Democrats only
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    # Resolve paths relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root  = os.path.join(script_dir, '..', '..')

    data_path    = os.path.join(repo_root, 'data',               'main_data_and_newsfeed_data.dta')
    pvals_main   = os.path.join(repo_root, 'regression_outputs', 'newsfeed_regression_p_values.csv')
    pvals_rep    = os.path.join(repo_root, 'regression_outputs', 'newsfeed_regression_p_values_rep.csv')
    pvals_dem    = os.path.join(repo_root, 'regression_outputs', 'newsfeed_regression_p_values_dem.csv')
    figure3_path = os.path.join(repo_root, 'figs',               'newsfeed_barchart_with_pvalues.pdf')

    # Load the Stata dataset (contains all participants)
    df_main = pd.read_stata(data_path)

    # --- Figure 3: full sample -------------------------------------------
    print("Creating main plot (Figure 3)...")
    create_plot(
        df=df_main,
        p_values_csv=pvals_main,
        output_filename='newsfeed_barchart_with_pvalues.pdf',
        plot_title_suffix='Main'
    )

    # --- Supplementary: Republicans and Independents sub-sample ----------
    print("Creating Republicans/Independents plot...")
    df_reps_indeps = df_main[df_main.partisanship_w1 != 'Democrat'].copy()
    create_plot(
        df=df_reps_indeps,
        p_values_csv=pvals_rep,
        output_filename='newsfeed_barchart_with_pvalues_reps_indeps.pdf',
        plot_title_suffix='Reps/Indeps'
    )

    # --- Supplementary: Democrats sub-sample -----------------------------
    print("Creating Democrats plot...")
    df_dems = df_main[df_main.partisanship_w1 == 'Democrat'].copy()
    create_plot(
        df=df_dems,
        p_values_csv=pvals_dem,
        output_filename='newsfeed_barchart_with_pvalues_dems.pdf',
        plot_title_suffix='Dems'
    )

    print("\nAll plots completed successfully!")

    # Auto-open Figure 3 in the OS default PDF viewer
    import subprocess, sys
    if sys.platform == 'darwin':
        subprocess.run(['open', figure3_path])
    elif sys.platform.startswith('linux'):
        subprocess.run(['xdg-open', figure3_path])
    elif sys.platform == 'win32':
        os.startfile(figure3_path)
