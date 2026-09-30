# Design Notes: Feature by Feature

These are the notes I wrote during the course: for each feature, how I implemented it and why I made each coding choice. The [main README](../README.md) gives the overview and the story behind the design.

## 1. Initial Program Behavior:
- Explanation of initial data form.
  The initial dataset is sourced as a csv file by using `pd.read_csv()` function. It includes 856274 observations and 72 variables, as indicated by `df.shape` output. The data seems to document car incidents within a geographical context, with detailed aspects (`df.columns`) related to coordinates (X, Y), crash details (crashSeverity), traffic condition (speedLimit), time series (crashYear), weather situation, vehicle types and potentially other contributing factors.

- Program behaviour regarding user inputs and outputs.
  This program consists of three main steps:
    Step 1: Run the procedure function main() to activate the program and manage the conditional steps. The `main()` function is executed to initialize the program and handle conditional logics.
    Step 2: Display a menu with options for generating a report, a placeholder for a graph, and an option to exit. If user selects option 0 from the displayed choices [0, 1, 2], this input will be validated by the `menu_select()` function, outputting the verified selection of option 1.
    Step 3: When the report option is selected, the program prompts the user to enter a specific year and speed limit. The report then displays the count of crashes by severity type for the selected year and speed limit. More detailed, the main() function uses the selected option as a condition to trigger the `read_csv_data()` and `print_crash_severity_report()` functions. The `unique_values()` function is utilized as a helper tool to generate the unique types of crashSeverity for looping through the severity counts. At this stage, the main() function specifically prompts the user to enter the desired crashYear and speedLimit. The print_crash_severity_report() function then applies these inputs as filter conditions to calculate the count of each crashSeverity type. 
    For example, if the user inputs the year 2000 and speed limit 30, the print_crash_severity_report() function generates a severity count report:
      Fatal Crash: 3
      Minor Crash: 28
      Non-Injury Crash: 231
      Serious Crash: 6

- There were two major shifts in my coding style throughout the project, particularly noticeable around week 5 and week 8.
    - Week 1 to Week 5:
        - My primary focus was simply to make the code functional. However, I encountered limitations due to my lack of familiarity with libraries like pandas and matplotlib.
    - Week 5 to Week 7 (the first major shift):
        - After watching Module 5 and reflecting on my struggles with excessive function complexity, I shifted my focus toward decomposing code for better elegance and readability. I realized that without clear structure, even I would get lost navigating my own functions.
    - Week 8 onward (the second major shift):
        - Inspired by the %>% pipeline in RStudio, I began thinking about "Pypelines" (my own term for Python-style pipelines). This sparked a transition to a more object-oriented programming (OOP) approach, where:
            - First, I aimed to design chains of class methods, allowing the output of one method to naturally feed into the next as the first argument.
            - Second, I worked on greatly improving clarity and readability. I modularized my code across multiple files, and structured imports carefully in main.py.
            - Third, I intentionally avoided unnecessary for loops, particularly for large datasets, and focused on leveraging vectorized operations from pandas and matplotlib to minimize time complexity.

## 2. Dependencies:
- Data (Waka Kotahi) CC BY 4.0
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Numpy](https://numpy.org/)
- [folium](https://python-visualization.github.io/folium)
- [Pyproj](https://pyproj4.github.io/pyproj/stable/)
- [requests](https://requests.readthedocs.io/en/latest/)
- [webbrowser](https://docs.python.org/3/library/webbrowser.html)
- [urllib.parse](https://docs.python.org/3/library/urllib.parse.html)
- [Random](https://docs.python.org/3/library/random.html)
- [time](https://docs.python.org/3/library/time.html)
- [os](https://docs.python.org/3/library/os.html)

## 3. How to Run:
To execute this program run following command from a terminal:

`python main.py`

## 4. Future Development:
### 1. Validate user input: Crash Severity Report (Basic Analysis Feature)
**How I Implemented This Feature**
- My implementation of input validation is based on two key ideas:
    - Standardized Comparison — Both the user input and the option list are first standardized before being compared, ensuring consistent and reliable validation.
    - OOP-Driven Menu Interaction — The validation process follows an object-oriented design: the menu displays itself, prompts the user for input, validates the input against either option indices or values, provides success or error feedback, and ultimately returns a validated user choice.
**The Coding Choices I Made and Why**
- Coding Choices for Option List Standardization:
    - Columns like crashYear or speedLimit often contain many values. To standardize valid options for user input, I created a Menu class. When passed a list, the initializer automatically applies dropna(), unique(), and tolist() in succession.
- Coding Choices for User Input Standardization:
    - I built a CleanInput class (a subclass of str) to flexibly cleanse user inputs. Currently used for fields like crashYear and speedLimit, it processes entries via CleanInput.general_style(), stripping whitespace and formatting inputs into standardized float-type strings. The class is designed to be expandable, allowing additional input-cleaning styles to be easily added in future projects.
- Coding Choices for Validation Process:
    - Once both options and inputs are standardized, the Menu.validate_with_index() method reliably validates user selections by direct comparison.
- Why the Coding Choices:
    - Philosophically, validation should compare standardized inputs against standardized options, not expect perfect inputs. 
    - Code-wise, an OOP approach was natural: encapsulating valid choices in a Menu object aligns with how validation fundamentally operates — by comparison.

### 2. Use Temporary Speed Limit if Defined Instead of Normal Speed Limit (Basic Analysis Feature)
**How I Implemented This Feature**
- To implement this feature, I introduced a new column in the crash dataframe called effectiveSpeedLimit. This column prioritizes the temporarySpeedLimit value if it is available; otherwise, it defaults to the speedLimit value.
- The rest of the report then uses effectiveSpeedLimit instead of speedLimit, so that any logic or filtering automatically respects temporary overrides.
**The Coding Choices I Made and Why**
- Coding Choices and Their Reasoning for Fallback Logic:
    - I created a df_with_effective_speed function to add an effectiveSpeedLimit column, prioritizing temporarySpeedLimit over speedLimit. Encapsulating this in a function ensures clear separation of concerns and improves code readability.
    - This new DataFrame is built inside core_crash_severity_data to provide a centralized, reliable foundation for future reporting and graphing. The implementation follows a "mutate and select" pattern to maintain data integrity.
- Coding Choices and Their Reasoning for combine_first():
    - Initially, I used .apply() with a custom is_numeric() check to capture a broader range of real-world data issues. However, after further analysis, I switched to combine_first() for this crash dataset because:
        - combine_first() naturally supports fallback logic (using the second value when the first is missing).
        - With 856,274 rows, its vectorized operations offer better scalability than row-by-row .apply().
        - Given that temporarySpeedLimit values are mostly clean (mostly valid numbers and occasional NaNs), combine_first() strikes the best balance between robustness and efficiency. Unique values in temporarySpeedLimit are [nan, 30.0, 70.0, 50.0, 40.0, 20.0, 80.0, 60.0, 10.0, 90.0, 45.0, 8.0, 100.0, 75.0, 65.0].
- The initial .apply() code I used before .combine_first():
```python
crash_dataframe["effectiveSpeedLimit"] = crash_dataframe.apply(
    lambda row: row["temporarySpeedLimit"] if is_numeric(row["temporarySpeedLimit"]) else row["speedLimit"],
    axis=1
)
``` 

### 3. Warn the User if No Records Are Found (Basic Analysis Feature)
**How I Implemented This Feature**
- A validation process after the user's selection determines whether any matching records exist. This ensures that even valid inputs, such as requesting a report for 2025, will not silently proceed if there is no actual data associated with them.
**The Coding Choices I Made and Why**
- Essentially, the year 2025 is compared against a list of valid years, with both values standardized as float-type strings. This comparison is handled by my custom function enhanced_numeric_selection, which processes user selections when a specific year is chosen as a report filter. The overall design of enhanced_numeric_selection allows it to universally catch similar mismatches across different columns, including crashYear, speedLimit, and even crashSeverity.
- On the interactive level, every menu-based input prompt includes a display stage before validation, following an object-oriented (OOP) validation chain implemented universally in Feature 1. However, if a user still enters an out-of-range value like 2025, despite seeing available options (e.g., 2000–2024), the error is caught by the validate_with_values method in the Menu class. In this case, an appropriate "no match" message is triggered to inform the user that no matching record exists for the selected year. The system then loops back, redisplaying the valid crashYear options for the user to make a new selection.
- To provide error messages, I centralized all feedback within the rand_msg() function inside the Menu class. This function handles different error and success scenarios, and for each error type, it offers multiple message variations selected randomly using random.choice(), helping avoid repetitive or monotonous prompts.

### 4. Add All Years Option — Crash Severity Report (Basic Analysis Feature)
**How I Implemented This Feature**
- I expanded the crash severity report filtering options by introducing an "All Years" selection. In the enhanced_numeric_selection function, when the user is prompted to choose a crash year, they can now select:
    - All crash years,
    - A year range, or
    - A specific year.
- If "All crash years" is selected, the system includes all available years from the dataset without requiring additional input.
**The Coding Choices I Made and Why**
- The overall structure of the crash_severity_report function follows a pipeline-style design, similar to the RStudio workflow:
    - report <- df %>% mutate() %>% select() %>% filter() %>% group_by() %>% summarize().
- Within this framework, the "All Years" option is implemented as part of the filtering stage, using .loc to apply row_conditions, which are constructed in list format. This design keeps the data transformation process modular and intuitive, allowing flexible user-driven filtering while maintaining the integrity of the reporting pipeline.
- I introduced a menu-driven structure within enhanced_numeric_selection to offer three distinct filtering paths: selecting all values, selecting a range of values, or selecting a single specific value. This structure aligns seamlessly with the broader feature set: supporting the "All Years" option for Feature 4, single-year selections for standard crash severity reports, and providing all-year data as the base for plotting crash trends over time in Feature 5.

### 5. Implement Crash Reports Over Time Graph (Basic Analysis Feature)
**How I Implemented This Feature**
- Initially, I considered building the Over Time Graph as a standalone function with its own separate user input prompts. However, after developing the enhanced_numeric_selection function for flexible year selection in the crash severity report, I realized that these two features could naturally be integrated into a unified workflow.
- enhanced_numeric_selection already allowed users to select across all years, a year range, or a specific year, and could also be easily reused to handle filtering by speed limits. The remaining challenge was enabling flexible user selection of crash severity types (e.g., Minor Crash, Non-Injury Crash).
- To solve this, I developed the enhanced_text_selection function, which mirrors the numeric selection structure but is specifically tailored for textual categories where range-based filtering does not apply. enhanced_text_selection provides users with two main options: selecting all crash types, or selecting one or multiple specific crash types. This unified design allows the report and the time series graph to share the same input selection architecture, ensuring consistency, flexibility, and scalability.
**The Coding Choices I Made and Why**
- Unifying Input Selection Across Features:
    - Rather than writing isolated input prompts for each feature, I built modular selection functions (enhanced_numeric_selection and enhanced_text_selection) that can be reused across different reporting and visualization tasks.
    - This ensures that any future additions or changes (such as adding more filter conditions) can be implemented consistently without redundant code.
- Seamless Slicing and Dicing Design Across Data Types:
    - I approached user input design from a slicing and dicing perspective: empowering users to flexibly partition the dataset according to their specific needs.
    - For numeric fields like crashYear and effectiveSpeedLimit, the enhanced_numeric_selection function enables three slicing options:
        - Selecting all values (no slicing),
        - Selecting a continuous range of values (e.g., years 2010–2015),
        - Selecting a specific single value (e.g., year 2022).
    - For categorical fields like crashSeverity, where range logic does not apply, I developed the enhanced_text_selection function to enable:
        - Selecting all available crash types,
        - Or slicing flexibly across multiple specific crash types (e.g., "Non-Injury Crash" and "Minor Crash" together).
    - By standardizing slicing and dicing across both numeric and text dimensions, the system provides a powerful, consistent user experience that supports a wide range of exploratory analysis needs.

### 6. Addtional Data Wrangling-Enriching: Data Online Update (Basic Analysis Feature)
**How I Implemented This Feature**
- The purpose of this feature is to add more meaningful rows to our existing crash dataset.
- To access the latest data from Waka Kotahi, I utilized the API provided on their official website. While they do offer the full dataset, their server enforces a maxRecordCount limit, which restricts the number of entries that can be retrieved per request. To work within this constraint and still ensure the dataset remains extensible and realistic, I implemented a dynamic online update feature. This feature automatically fetches the most recent crash data from the Crash Analysis System (CAS) in chunks, adapting to the server's request limit. By doing so, the program keeps the local dataset current while respecting the API’s usage policies.
    - The method CrashDf.df_loaded_with_online_update() acts as the entry point for this enrichment process.
    - It first loads the local dataset and then checks online to see if newer entries are available.
    - If yes, it requests additional data and appends it to the local dataframe.
    - The updated data is then passed through two enrichment steps:
        - Add effective speed column (e.g., using temporarySpeedLimit and speedLimit)
        - Mutate projected coordinates (X, Y) into longitude/latitude
- This step ensures that the crash dataset stays up-to-date, map-ready, and analysis-friendly.
**The Coding Choices I Made and Why**
- Layered Function Design (Decomposition)
    - I broke the workflow into multiple smaller functions:
        - `_df_from_online_requests()` — handles update logic
        - `_df_of_n_entries_per_request()` — limits the number of rows per request
    - This improves modularity and code reuse while isolating the logic for easier debugging and scaling.
- Comparing Primary Keys
    - I compare max_local_pk (last row in local file) and maxpk_online (latest row online) to determine whether new data exists.
    - This comparison minimizes unnecessary API calls and ensures efficiency.
- Flexible Request Size
    - The method uses a default of 2000 rows per request, but this can be overridden when needed.
    - This gives me control over performance when testing or operating in different environments.
- Informative Logging
    - I added print() logs with progress markers (e.g., progress: {current}/{total}) so users understand:
        - Whether data is updating
        - How many rows were fetched
        - When it’s complete
    - This improves transparency and debuggability.
- In-Session Only (No Save to File)
    - New rows are loaded into memory only (not saved to disk).
    - This allows the process to be repeatable and demonstrable each time the project runs (great for presentations or learning).
- Efficient Merging
    - Used pd.concat() and combine_first() to merge local and remote datasets while preserving data integrity.
- Coordinate Enrichment
    - I used pyproj to convert X, Y into accurate lon/lat, ensuring clean map plots.
    - This spatial transformation is essential for interactive map features like Folium.

### 7. Addtional Data Wrangling-Enriching: Mutate Longitude/Lattitude based on X/Ys (Student Lead Feature)
**How I Implemented This Feature**
- To make the dataset map-ready, I implemented a transformation that converts the existing projected X/Y coordinates into geographic longitude/latitude. This spatial enrichment step ensures compatibility with mapping libraries like Folium, which require standard geographic coordinates.
    - The transformation uses the pyproj library to convert from New Zealand’s projected CRS (EPSG:2193) into the global geographic CRS (EPSG:4326).
    - A helper method, DSDf.meterbounds_for_projected_country(), calculates the valid bounds for filtering and also helps define the source and target CRS for conversion.
**The Coding Choices I Made and Why**
- CRS-Aware Transformation
    - I used pyproj.Transformer.from_crs().transform() to perform the conversion accurately and efficiently.
    - This ensures that X/Y values are translated into true geographic coordinates rather than relying on rough approximations.
- Column-Wise Enrichment
    - Just like the effectiveSpeedLimit, this feature adds new columns (lon, lat) to the dataset, instead of overwriting existing ones — preserving the original data while enabling geographic visualization.
- Improved Visualization Compatibility
    - The result is a dataset that can be directly used in interactive maps like heatmaps, pinmaps, and cluster maps — all of which rely on latitude and longitude as input.

### 8. Addtional Data Wrangling-Cleaning: Remove entries with Inaccurate Longitude/Lattitude values (Student Lead Feature)
**How I Implemented This Feature**
- This feature removeS certain rows from our existing crash dataset.
- To ensure the accuracy of location-based analysis and mapping, I added a cleaning step to remove entries with invalid or misleading coordinate values. Although X/Y values may exist, they aren’t always reliable — especially if they fall outside the official geographic bounds of New Zealand to the other side of the world map, and distort our mapping visualisation.
- This step takes the previously enriched dataset and filters out geometrically implausible rows, improving map precision and analysis quality.
**The Coding Choices I Made and Why**
- Reference Library Over Reinventing the Wheel
    - By using a specialized reference library like pyproj, the coordinate transformation is far more accurate and efficient than my earlier ideas — such as using IQR boxplots to detect X/Y outliers. 
    - This approach avoids the guesswork and limitations of statistical bounding methods, which can be misleading — especially in countries like New Zealand, where crash events are asymmetrically distributed due to both geographic features (like mountains and coastlines) and domestic factors (such as population clusters, infrastructure, and road design).
    - Using formal CRS definitions ensures our spatial boundaries reflect the real-world context, making filtering more robust and relevant.
- Encapsulation in a Utility Method
    - I created a reusable function that returns the meter bounds for a given country (like NZ), so this logic is cleanly abstracted and extendable to other countries in the future.

### 9. Visualisation Feature: Fatal Crash Heatmap (Student Lead Feature)
**How I Implemented This Feature**
- To visualize the spatial and temporal patterns of fatal crashes, I developed an animated heatmap using the Folium library.
    - The function `plot_crash_heatmap()` prepares the heatmap data grouped by year and displays it with HeatMapWithTime, allowing viewers to watch crash density evolve over time.
    - The background map is generated dynamically using the `map_background()` function, which centers the map based on the dataset's geographic extent (lat, lon).
    - Once rendered, the final output (fatal_heatmap_with_year.html) is saved and automatically opened in a browser tab for immediate review.
**The Coding Choices I Made and Why**
- Used Folium for Interactive Mapping
    - Folium was chosen over static plotting libraries (like Matplotlib or Seaborn) because it supports interactive features, auto-play, and layered zoom, which are far more user-friendly and insightful for spatial-temporal data.
- Grouped Heatmap by Year
    - I grouped the coordinates by crashYear, which lets the heatmap play year by year — giving a clear visual of how fatal crash patterns changed over time.
- Custom Map Centering
    - Instead of hardcoding a fixed map center, the map_background() function dynamically calculates the center using the min/max of the dataset's coordinates — this ensures the map always fits the data.
- Animation with Time Index
    - I used a list comprehension to build heat_data for each year and matched it with a string-formatted year index to serve as the animation timeline.
- Map Usability Enhancements
        - auto_play=True: Allows smooth timeline playback.
        - max_opacity=0.6: Avoids visual over-saturation.
        - radius=10: Adjusted for the crash density appearance.
        - auto_save_open(): Automatically opens the map in a browser for easy viewing.
- Encapsulation & Readability
    - The logic is split into clear steps (background, data grouping, time index, visual rendering) for better maintainability and reuse in future visualizations.

### 10. Visualisation Feature: Exploratory Crash Pinmap (Student Lead Feature)
**How I Implemented This Feature**
- To support exploratory crash analysis at an individual incident level, I implemented an interactive pinmap using Folium’s DualMap plugin.
    - The function plot_crash_pinmap() filters the data to focus on serious and fatal crashes to reduce memory usage and highlight meaningful incidents.
    - Each pin displays detailed crash information via HTML-formatted tooltips, including crash year, location, weather, severity, and involvement of trees or motorcycles.
    - The map features both a light (OpenStreetMap) and dark (CartoDB Dark Matter) background, allowing users to compare readability under different themes.
    - Users can interact with the map via layer controls (to toggle severity types) and a search bar (Geocoder) for specific locations.
**The Coding Choices I Made and Why**
- Dual Map Background for Better Comparison
    - I used folium.plugins.DualMap() to offer side-by-side visual comparison of crashes in light vs dark themes, giving users a better UI experience depending on context or personal preference.
- Severity-Based Filtering
    - To optimize performance and focus the analysis, I filtered the dataset to only include ‘Serious Crash’ and ‘Fatal Crash’ cases. This avoids clutter and draws attention to more critical incidents.
- Dynamic HTML Popups for Detail
    - Each marker is linked to an HTML-formatted popup displaying key crash attributes. This creates an informative, user-friendly display for case-by-case inspection — ideal for investigative or operational review.
- FeatureGroup Organization
    - Pins are grouped by severity within each map panel (fg_bright, fg_dark) using folium.FeatureGroup(). This makes it easy to manage and toggle layers using folium.LayerControl().
- Location-Aware Centering
    - The map automatically centers based on the dataset’s geographic midpoint, avoiding the need for hardcoded coordinates — enhancing flexibility and reusability.
- Enhanced Interactivity
    - I added folium.plugins.Geocoder() to allow users to search by location, improving map usability and real-world application potential.
- Automatic Output
    - Finally, the map is saved to an HTML file and automatically opened in the browser for quick review using auto_save_open().

### 11. Visualisation Feature: Exploratory Crash Clustermap (Student Lead Feature)
**How I Implemented This Feature**
- To improve spatial readability and reduce map clutter from individual pins, I created a cluster-based map using Folium’s MarkerCluster plugin.
    - The function plot_crash_cluster_map() displays all crash severity types (Non-Injury, Minor, Serious, Fatal) using a grouped marker system.
    - Each marker in a cluster shows detailed crash data on click, presented in a styled HTML popup.
    - Markers are categorized and styled based on crash severity, and layer controls allow toggling visibility by category.
    - A Geocoder plugin was added for users to quickly find specific locations, enhancing exploration.
**The Coding Choices I Made and Why**
- Marker Clustering to Improve Performance
    - Instead of plotting thousands of individual points, I used MarkerCluster to group nearby crashes and reduce visual overload. This greatly enhances both performance and usability on dense maps.
- Severity-Based Icons for Visual Clarity
    - I assigned each crash severity a distinct Font Awesome icon (smile-o, wrench, exclamation-triangle, skull) via BeautifyIcon, making each category immediately distinguishable at a glance.
- Rich HTML Popups
    - Each marker displays a full HTML-formatted summary of the crash using a responsive Bootstrap-style table, giving users detailed incident-level insights without overwhelming the map.
- Categorized Clusters for Layer Control
    - Clusters are grouped by severity level, and folium.LayerControl() allows users to toggle visibility — ideal for comparative severity analysis.
- Location Search Integration
    - I added folium.plugins.Geocoder() so users can jump to specific locations, making the map more practical for real-world investigation or reporting.
- Modular Design
    - The function is modular and scalable — future additions like filtering by date or weather could be integrated easily with minimal disruption to existing logic.
- Automatic Output
    - The final map is saved and auto-launched in a web browser, ensuring smooth presentation and demonstration.

### 12. OOP Coding Framework: Object-Oriented Refactoring (Student Lead Feature)
**How I Implemented This Feature**
- To improve modularity, scalability, and maintainability of the project, I refactored the original procedural code into an Object-Oriented Programming (OOP) structure by defining custom classes and subclasses:
    - I introduced a base class called DSDf (Data Science DataFrame), which extends pandas.DataFrame and serves as a reusable foundation for data-centric projects.
    - Then, I created domain-specific subclasses such as CrashDf, CrimeDf, and NYCDf, each inheriting from DSDf and adding methods tailored to their respective data contexts (e.g., crash cleaning, clustering, enrichment). This project only focuses on CrashDf, other subclasses here are just place holders for future use.
    - I also built separate feature modules (e.g., Crash Features) to encapsulate functional logic and chain class methods into higher-level workflows.
    - Finally, a clean main() driver was designed for each subclass to demonstrate their use.
**The Coding Choices I Made and Why**
- Modular Design for Reusability
    - By separating general functionality into DSDf and domain-specific behaviors into subclasses like CrashDf, the code became easier to extend, reuse, and adapt to other datasets.
- Encapsulation for Clarity
    - Each class now contains only the methods relevant to its scope. CrashDf may include geometry cleaning and severity filtering, while CrimeDf can handle different aggregation rules. This makes the structure intuitive and logically clean.
- Chaining via Feature Modules
    - I offloaded chained operations (e.g., enriching → cleaning → visualizing) into standalone feature modules, acting like a factory to assemble method calls from the class — this supports a plug-and-play architecture.
- Inheritance from Pandas
    - DSDf inherits from pandas.DataFrame, so all default pandas behaviors are preserved, while allowing me to inject custom utilities for things like metadata, bounds detection, or map readiness.
- Scalable to Multiple Domains
    - This design proved scalable — I used the same OOP structure for different datasets (crash, crime, NYC311) with minimal duplication, just by defining new subclasses and methods.
- Centralized Main Entrypoints
    - Each domain (e.g., crash, crime) will have a clean main() that calls class methods in sequence. This makes the program easier to test, demo, and debug — and helps enforce separation of concerns.

## Citations
- Waka Kotahi. _Crash Analysis System (CAS) data_ [Review of  Crash Analysis System (CAS) data]. Retrieved January 13, 2025, from https://opendata-nzta.opendata.arcgis.com/datasets/8d684f1841fa4dbea6afaefc8a1ba0fc_0/explore
- Folium Developers. Folium: Python Data. Leaflet.js Maps. [Python library for interactive map visualizations]. Retrieved January 13, 2025, from https://python-visualization.github.io/folium
