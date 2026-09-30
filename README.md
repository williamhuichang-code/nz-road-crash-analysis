# NZ Road Crash Analysis Tool (Python, OOP)

An interactive Python tool for exploring **856,000+ New Zealand road crashes** from Waka Kotahi's Crash Analysis System: it keeps the data up to date through the live API, cleans it, and turns it into crash-severity reports, trend graphs and interactive maps.

Built for the University of Canterbury course *Computer Programming* (COSC480, grade A+). What started as a simple script grew into a small object-oriented framework, and building it changed how I think about code. That story is [below](#how-this-project-changed-the-way-i-code).

**▶ Explore the interactive maps:** [fatal crash heatmap (animated by year)](https://williamhuichang-code.github.io/nz-road-crash-analysis/data/fatal_heatmap_with_year.html) · [serious and fatal crash pinmap](https://williamhuichang-code.github.io/nz-road-crash-analysis/data/pinmap_bright_dark.html) · [severity cluster map](https://williamhuichang-code.github.io/nz-road-crash-analysis/data/cluster_map_for_severity.html)

| Fatal crash heatmap (animated by year) | Serious and fatal crashes, light and dark maps |
|---|---|
| ![Fatal crash heatmap](screenshots/heatmap.png) | ![Crash pinmap](screenshots/pinmap.png) |
| **Severity cluster map, with a crash pop-up** | **Menu-driven report and trends graph** |
| ![Crash cluster map](screenshots/clustermap.png) | ![Crash report and trends graph](screenshots/report_and_trends.png) |

## What it does

Run the program and a menu guides you through:

| Feature | What you get |
|---|---|
| **Crash severity report** | Crash counts by severity for any year and speed limit: all values, a range (e.g. 2010–2015) or a single value, and any combination of severity types |
| **Crash trends graph** | The same selections plotted over time (matplotlib) |
| **Fatal crash heatmap** | An animated Folium heatmap showing how fatal crash hotspots change year by year |
| **Crash pinmap** | Serious and fatal crashes as pins with detailed pop-ups (year, location, weather, and whether trees or motorcycles were involved), side-by-side light and dark maps, and location search |
| **Crash cluster map** | All severities grouped into clusters with severity icons and layer toggles, readable even with thousands of points |

Behind the menu, the data goes through several automatic steps:

- **Live update:** checks the Waka Kotahi API for crashes newer than the local file and downloads them in chunks, respecting the server's record limit.
- **Effective speed limit:** uses the temporary speed limit where one applies, otherwise the normal limit.
- **Coordinates:** converts NZTM metres (EPSG:2193) to longitude/latitude (EPSG:4326) with pyproj, so the data works with web maps.
- **Cleaning:** removes crashes whose coordinates fall outside New Zealand's official bounds.
- **Input validation:** every prompt shows the valid options, standardises what you type, and explains what went wrong if it can't be matched (for example, a year with no records).

## What the maps suggest

Exploring the maps pointed to a few patterns (visual, exploratory observations rather than statistical tests):

- **Fatal crashes cluster in two kinds of places:** densely populated urban areas, and open rural roads with high speed limits. The overall pattern stays similar from year to year.
- **Darkness matters:** on the side-by-side pinmap, fatal crashes appear more often in dark conditions.
- **State Highway 1 north of Wellington** shows a noticeable concentration of fatal crashes compared with other stretches.
- **Motorcycles and trees:** looking at individual crashes, fatal crashes more often involve a motorcycle or a tree than crashes of lower severity.

## How it's designed

![My general framework for data science projects using OOP](screenshots/framework.png)

- **`DSDf`** extends `pandas.DataFrame` with general data science steps, such as coordinate conversion and helpers that print or pause *inside* a method chain. It keeps its own type after slicing, so a filtered `DSDf` is still a `DSDf`.
- **`CrashDf`** adds everything specific to the crash data: loading with the live API update, the effective speed limit and cleaning by NZ bounds. `CrimeDf` and `NYCDf` are placeholders showing how the same base could serve other datasets.
- **`Menu`** and **`CleanInput`** handle all user interaction in one consistent way.
- **Feature functions** (`module_crashdf_features.py`) chain these methods into reports and maps, and **`main.py`** only runs the menu.

I held every part to the same five goals: **fast, raises no error, user friendly, informative, and extendable.** For example, the data loads once and the menu then loops without reloading; every input is checked, but the program tolerates reasonable variations in what people type.

Why it's built around method chains is the story of the next section.

## How this project changed the way I code

My coding style went through three stages during this project, and each one changed how I think about writing code.

**1. Making it work (weeks 1–5).** At first my only goal was working code. I was still learning pandas and matplotlib, and functions grew long as I added features. Before long, I was getting lost in my own code.

**2. Making it readable (weeks 5–7).** I started breaking large functions into small ones, each doing one thing. The code became easier to read and test, and I began to see repeated patterns across features.

**3. From nested brackets to "Pypelines" (week 8 onwards).** The turning point was noticing that my decomposed code looked like a maths equation full of nested brackets:

```python
# nested: read from the innermost bracket outwards, passing arguments down every layer
report(filter(clean(enrich(load(file), speed_col), bounds), year, speed), severity)
```

As in maths, you have to start from the innermost bracket and work outwards. And the more I decomposed my functions, the worse it got: every layer had to receive arguments only to pass them further down, which was painful to write and even harder to read.

Then R's pipe gave me the idea. In R, `df %>% mutate() %>% filter() %>% summarise()` lets data flow through steps in the order you think about them. I wanted the same in Python and called it "Pypelines". The answer was object-oriented programming: if each method works on the object and returns it, you can start from the core and chain every step outwards, like `core.(1).(2).(3)`:

```python
# chained: read left to right, each step works on the object itself
CrashDf.df_loaded_with_online_update(file).cleaned_crashdf_by_nz_bounds()
Menu(options).display_with_index().general_prompt().validate_with_index()
```

No more passing arguments all the way down, because the data travels inside the object. That idea shaped everything else:

- **Objects that operate on themselves.** I made the DataFrame the object: `DSDf` extends pandas, so a crash dataset can *enrich itself, clean itself and describe itself*, and every step reads in order.
- **The menu became an object too.** A menu displays itself, prompts for input, validates it and returns a clean answer.
- **Framework over script.** Because general behaviour lives in `DSDf` and crash-specific behaviour in `CrashDf`, the structure can serve a different dataset just by adding a subclass. For the first time I was designing something reusable, not only solving this one assignment.

A few lessons I still use:

- **Standardise before you compare.** Good validation doesn't expect perfect input. It cleans both the user's input and the valid options into the same form, then compares them.
- **Build once, reuse everywhere.** The same selection functions (all values, a range or a single value) drive both the report and the trends graph, so a new filter only needs to be written once.
- **Think in columns, not loops.** With 856,000 rows, I replaced a row-by-row `.apply()` with the vectorised `combine_first()` for the speed-limit fallback.
- **Use the right reference instead of guessing.** I first thought of finding bad coordinates with boxplot outliers. Instead I used the official coordinate system definitions (pyproj), which reflect New Zealand's real boundaries.

This way of thinking carried into later projects. In [DSI Studio](https://github.com/williamhuichang-code/shiny-dsi-studio), my R Shiny app, I built the same idea at a larger scale: 45+ modules and a chained data pipeline where each stage passes its output to the next.

The detailed notes behind each feature, including how I implemented it and why I chose each approach, are in [docs/design-notes.md](docs/design-notes.md).

## Run it locally

1. Install Python 3.9+ and the packages: `pip install -r requirements.txt`
2. Download the full dataset (CSV) from [Waka Kotahi's Crash Analysis System](https://opendata-nzta.opendata.arcgis.com/datasets/8d684f1841fa4dbea6afaefc8a1ba0fc_0/explore) and save it as `data/Crash_Analysis_System_(CAS)_data.csv`. To keep it somewhere else, set the environment variable `CRASH_DATA_DIR` to that folder.
3. Run `python main.py` and follow the menu.

Each time it starts, the program downloads any crashes added since your copy, for that session only. Maps are saved to `data/` and open in your browser.

## Repository contents

```
main.py                      menu and program entry point
class_dsdf.py                DSDf: DataFrame base class for data science steps
subclass_crashdf.py          CrashDf: crash-specific loading, API update and cleaning
subclass_crimedf.py,         placeholders showing how other datasets
subclass_nycdf.py              would reuse the framework
class_helper_menu.py         Menu: display, prompt and validate
class_helper_clean_input.py  CleanInput: standardises user input
module_crashdf_features.py   reports, trends graph and maps
data/                        generated interactive maps (HTML)
docs/design-notes.md         feature-by-feature implementation notes
screenshots/                 images used in this README
```

## Next steps

- Add unit tests (pytest) for the class methods and run them automatically with GitHub Actions.
- Complete `CrimeDf` and `NYCDf` to show the framework on other datasets.

## Credits

- Data: [Waka Kotahi NZ Transport Agency, Crash Analysis System (CAS)](https://opendata-nzta.opendata.arcgis.com/datasets/8d684f1841fa4dbea6afaefc8a1ba0fc_0/explore), CC BY 4.0.
- Maps: [Folium](https://python-visualization.github.io/folium) (Leaflet.js); coordinates: [pyproj](https://pyproj4.github.io/pyproj/stable/).
- Course: COSC480 Computer Programming, University of Canterbury.
