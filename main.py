"""This program is designed to cleanse data, organize, identify trends and
visualize data for ill-specified, complex data-science problems.
   Author: William Hui Chang
   Date: Fri Mar 21 21:06:21 2025
"""


from class_helper_menu import Menu
from subclass_crashdf import CrashDf
from module_crashdf_features import core_crash_severity_data, crash_severity_report, plot_crash_trends
from module_crashdf_features import core_crash_heatmap_data, plot_crash_heatmap, plot_crash_pinmap, plot_crash_cluster_map
from module_helper import print_divider, pause


def end_of_application() -> bool:
    """Ends the application."""
    print(Menu.rand_msg("bye msg"))
    return True


def general_validation_loop(validation_func: callable) -> str:
    """ Loops a validation function and returns a valid choice. """
    valid_selection = None
    while valid_selection == None:
        valid_selection = validation_func()
    return valid_selection


def main_menu_validation_trial() -> str:
    """ Returns a potential menu selection for looping after a chained function process. """
    main_menu = ["Exit", 
                 "Crash Severity Report", 
                 "Crash Reports Over Time Graph", 
                 "Fatal Crash Heatmap", 
                 "Exploratory Crash Pinmap", 
                 "Exploratory Crash Clustermap"]
    return Menu(main_menu).display_with_index().general_prompt().validate_with_index()


def main():
    """ Generates reports and graphs based on crash data. """
    # load df
    initialized_raw_df = CrashDf.df_loaded_with_online_update(CrashDf._crash_csv_name)
    if initialized_raw_df is None:
        return  # data file missing: the message above explains where to put it
    crash_severity_core_df = core_crash_severity_data(initialized_raw_df)
    core_hm_df = core_crash_heatmap_data(initialized_raw_df)
    # main menu loop
    terminate = None
    while terminate != True:
        # menu selection validation
        menu_selection = general_validation_loop(main_menu_validation_trial)
        # match choice scenarios
        if menu_selection == "Exit":
            terminate = end_of_application()
        elif menu_selection == "Crash Severity Report":
            crash_report = crash_severity_report(crash_severity_core_df)
            print(crash_report)
        elif menu_selection == "Crash Reports Over Time Graph":
            report_for_plot = crash_severity_report(crash_severity_core_df)
            plot_crash_trends(report_for_plot)
        elif menu_selection == "Fatal Crash Heatmap":
            print_divider()
            print("Just showing fatal crashes for now — it helps keep things light on memory!")
            pause()
            plot_crash_heatmap(core_hm_df[core_hm_df['crashSeverity'] == 'Fatal Crash'])
        elif menu_selection == "Exploratory Crash Pinmap":
            print_divider()
            print("Only fatal and serious crashes are shown, limited to the most recent 10,000 entries to reduce memory load.")
            pause()
            plot_crash_pinmap(core_hm_df.tail(10000))
        elif menu_selection == "Exploratory Crash Clustermap":
            print_divider()
            print("Limited to the most recent 5,000 entries to reduce memory load.")
            pause()
            plot_crash_cluster_map(core_hm_df.tail(5000))



if __name__ == "__main__":
    main()
