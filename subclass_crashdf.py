"""This module is designed for a subclass of DSDf, called CrashDf, means crash severity dataframe.
   Author: William Hui Chang
   Date: Sat May 24 09:59:08 2025
"""

from class_dsdf import DSDf
import os
import pandas as pd_crash
import numpy as np_crash
import requests as requests_crash
from module_helper import pause, print_divider
import folium
import webbrowser
from folium.plugins import HeatMapWithTime


class CrashDf(DSDf):
   """
    A crash df subclass that inherits from DSDf, and
   can operate itself, enrich itself, wrangle itself etc. 
   """
   # class constants
   # local crash file name for git launching and local testing
   _crash_csv_name = r"Crash_Analysis_System_(CAS)_data.csv"
   # folder holding the local csv: set CRASH_DATA_DIR, or place the file in ./data
   _data_dir = os.environ.get("CRASH_DATA_DIR", "data")
   # for online update, common url part
   _common_url_part = r"https://services.arcgis.com/CXBb7LAjgIIdcsPt/arcgis/rest/services/CAS_Data_Public/FeatureServer/0"
   # for online update, primary key of crash data
   _crash_pk = 'OBJECTID'

   # constructor
   @property
   def _constructor(self):
      # after slicing or dicing, make it return a CrashDf instead of a DSDf
      return CrashDf
   
   # initializer based upon upper class DSDf
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

   # instance method
   def _local_maxpk(self):
      """ Gets the max local primary key. """
      if CrashDf._crash_pk not in self.columns:
         raise KeyError(f"'{CrashDf._crash_pk}' not found in DataFrame columns.")
      return self[CrashDf._crash_pk].max()
   def _df_of_n_entries_per_request(self, max_local_pk, nrows=2000, sorting="asc") -> pd_crash.DataFrame:
      """ Returns 1 to 2000(default) online entries from one request as pd df. """
      update_url = (
         f"{CrashDf._common_url_part}/query"
         f"?where={CrashDf._crash_pk}>{max_local_pk}"
         f"&outFields=*"
         f"&orderByFields=OBJECTID {sorting}"
         f"&resultRecordCount={nrows}"
         f"&f=json"
         )
      # the HTTP response
      http_response = requests_crash.get(update_url, timeout=30)
      # .json() converts the HTTP response into a nested Python list of dicts
      payload = http_response.json()
      if 'error' in payload:
         raise RuntimeError(payload['error'].get('message', payload['error']))
      nested_attribute_list = payload.get('features', [])
      all_attributes = []
      for attribute in nested_attribute_list:
         split_dict_of_geometry = attribute.pop('geometry')
         split_dict_of_geometry = {k: np_crash.round(np_crash.float64(v), 0) for k, v in split_dict_of_geometry.items()}
         x = split_dict_of_geometry.get('x')
         y = split_dict_of_geometry.get('y')
         attribute.get('attributes').update({"X": x, "Y": y})
         all_attributes.append(attribute.get('attributes'))
      entries_per_query = pd_crash.DataFrame(all_attributes)
      return entries_per_query
   def _df_from_online_requests(self) -> pd_crash.DataFrame:
      """ Combines new results from all requests and returns as pd df. """
      print_divider()
      ### step 0, max local pk from local file and online pk from url, for comparison
      max_local_pk = self._local_maxpk()
      # the newest online entry beyond the local file; empty if already up to date
      try:
         latest_online = self._df_of_n_entries_per_request(max_local_pk, nrows=1, sorting="desc")
      except Exception as err:
         print(f"[Data Enriching] Online update skipped — the crash data service could not be reached ({err}).")
         print("Continuing with the local data.")
         pause()
         return CrashDf(pd_crash.DataFrame())
      if latest_online.empty or CrashDf._crash_pk not in latest_online.columns:
         print("You're all caught up — no newer crashes online, continuing with the local data.")
         pause()
         return CrashDf(pd_crash.DataFrame())
      maxpk_online = latest_online.loc[0, CrashDf._crash_pk]
      ### step 1, make requests until new entries are exhausted
      df_for_new_entries = pd_crash.DataFrame()
      if max_local_pk < maxpk_online:
         print("[Data Enriching] (automatic) Now heads up! Fresh data is available from the Crash Data Source — let’s grab them ...")
         pause()
         print("Note: New updated entries will be loaded into the session, but won't be saved locally")
         print("      — this way, the update process can be demonstrated each time when loading the project.")
         print_divider()
         pause()
      print(f"... requesting new entries..., {CrashDf._crash_pk} progress: {max_local_pk}/{maxpk_online}.")
      pause()
      while max_local_pk < maxpk_online:
         _df_of_n_entries_per_request = self._df_of_n_entries_per_request(max_local_pk)
         if _df_of_n_entries_per_request.empty:
            break  # nothing more returned, stop instead of looping forever
         df_for_new_entries = pd_crash.concat([df_for_new_entries, _df_of_n_entries_per_request], axis=0)
         n_collected = df_for_new_entries.shape[0]
         max_local_pk = df_for_new_entries[CrashDf._crash_pk].max()
         print(f"{n_collected} new entries collected, {CrashDf._crash_pk} progress: {max_local_pk}/{maxpk_online}.")
      # step 2, gets the df with new entries
      print_divider()
      print("You're all caught up — nothing new to fetch!")
      return CrashDf(df_for_new_entries)
   def _df_with_effective_speed(self) -> pd_crash.DataFrame:
      """ Return new crash df with effective speed limit. """
      print_divider()
      print("[Data Enriching] (automatic) New columns effectiveSpeedLimit added the crash dataset, ")
      print("which prioritizes temporarySpeedLimit and uses speedLimit as a fallback. ")
      pause()
      self = self.assign(effectiveSpeedLimit = 
            lambda df: df['temporarySpeedLimit'].combine_first(df['speedLimit']))
      return self
   def cleaned_crashdf_by_nz_bounds(self) -> pd_crash.DataFrame:
      """ Sifts through the data to keep only crashes within NZ's meter-based bounds. """
      print_divider()
      print("[Data Wrangling] Now cleaning those weird geometry entries in the dataset...\nHang tight, almost there ...\n...")
      pause()
      # nrows before cleaning
      nrow_before = self.shape[0]
      # bounds from DSDf's method
      nz_bounds = CrashDf.meterbounds_for_projected_country("New Zealand")
      # subset clean data
      self = self[
         (self['X'] >= nz_bounds['x_bounds'][0]) & 
         (self['X'] <= nz_bounds['x_bounds'][1]) & 
         (self['Y'] >= nz_bounds['y_bounds'][0]) & 
         (self['Y'] <= nz_bounds['y_bounds'][1])
      ]
      # nrows after cleaning
      nrow_after = self.shape[0]
      nrow_dirty = nrow_before - nrow_after
      print(f"{nrow_dirty} messy entries with strange coordinates removed. \nCoordinates clean and ready to roll!")
      pause()
      return self

   # class method

   # static method
   @staticmethod
   def local_df_loaded_with_filename(local_csv_name: str) -> pd_crash.DataFrame:
      """ Load local data and assign a customized df type for it. """
      print_divider()
      print("Now loading ...\n...")
      ### step 0, local parameters
      pathed_csv = os.path.join(CrashDf._data_dir, local_csv_name)
      local_raw_df = pd_crash.read_csv(pathed_csv)
      local_df_classed_with_ds = CrashDf(local_raw_df)
      print(f"Dataframe {local_csv_name} has been successfully loaded!")
      return local_df_classed_with_ds
   @staticmethod
   def df_loaded_with_online_update(local_csv_name: str) -> pd_crash.DataFrame:
      """ Returns dataframe loaded with auto-online-update from API. """
      print()
      print_divider()
      print("Now loading ...\n...")
      ### step 0, local parameters
      pathed_csv = os.path.join(CrashDf._data_dir, local_csv_name)
      ### refuse to update if local csv file not initialized
      try:
         ### step 1, load local df and get requested_df from online API
         local_df = CrashDf(pd_crash.read_csv(pathed_csv))
         requested_df = local_df._df_from_online_requests()
         ### step 2, concat and return
         df_enriched_with_update = pd_crash.concat([local_df, requested_df], axis=0).reset_index(drop=True)
         # effective speed implemented as a new column for the crash dataset by default
         df_enriched_with_effective_speed = CrashDf(df_enriched_with_update)._df_with_effective_speed()
         df_enriched_with_lon_lat = df_enriched_with_effective_speed._xy_mutate_lonlat()
         return df_enriched_with_lon_lat
      except FileNotFoundError:
         print("\nLoading/Updating Request Refused:")
         print(f"    '{local_csv_name}' was not found in the expected path.\n")
         print("Recommendation:")
         print("    Please download the full dataset once and place it in the right path.")
         print("    Incremental updates will be applied automatically every time the project is launched.\n")
         return None



if __name__ == "__main__":
   df = CrashDf.df_loaded_with_online_update(CrashDf._crash_csv_name).cleaned_crashdf_by_nz_bounds()
   df = df[df['crashSeverity'] == 'Fatal Crash']
   print_divider()
   print(df)
   # chang df into gdf for geo markers
   # geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
   # gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
   
   # lat_mbound and lon_mbound decide where the map start to show
   lat_mbound = (df['lat'].max() + df['lat'].min())/2
   lon_mbound = (df['lon'].max() + df['lon'].min())/2

   # maps
   # tiles="OpenStreetMap" for daytime
   # tiles="Cartodb dark matter" for night
   # zoom_start=12 for city, 6 for country
   m = folium.Map(location=[lat_mbound, lon_mbound], 
               zoom_start=6,
               tiles="OpenStreetMap") 
   # timed_heatmap step 1: Prepare heatmap data grouped by year
   years = sorted(df['crashYear'].dropna().unique())
   heat_data = [
      df[df['crashYear'] == year][['lat', 'lon']].dropna().values.tolist()
      for year in years
   ]
   # timed_heatmap step 2: generate time index (just use year labels)
   time_index = [str(year) for year in years]

   # timed_heatmap Step 3: Create animated heatmap
   HeatMapWithTime(
      data=heat_data,
      index=time_index,
      auto_play=True,
      max_opacity=0.6,
      radius=10
   ).add_to(m)

   # folium.GeoJson(
   #    gdf, 
   #    name = "crashSerity",
   #    marker=folium.Circle(radius=20, fill_color="orange", fill_opacity=0.4, color="black", weight=1),
   #    zoom_on_click=True,
   # ).add_to(m)


   # # markers
   # for _, row in df.iterrows():
   #    folium.Marker(
   #       location=[row['lat'], row['lon']],
   #       popup=row['OBJECTID'],
   #       icon=folium.Icon(color='red')
   #       ).add_to(m)

   # show map
   m.save(r"D:\DS\Py code\crash_map_testing_1.html")
   webbrowser.open_new_tab(r"D:\DS\Py code\crash_map_testing_1.html")

   # updated_crash_df = updated_crash_df.cleaned_crashdf_by_nz_bounds()
   # updated_crash_df = updated_crash_df._df_with_effective_speed()
   
   # print(updated_crash_df["crashYear"].unique())
   # print(type(updated_crash_df))
   
   # print(type(updated_crash_df))
   # print(updated_crash_df.tail())

   
   # max_local_pk_number = classed_local_crash_df.maxpk_existed
   # print(max_local_pk_number)

   # print(classed_local_crash_df._df_of_n_entries_per_request())

   # print(classed_local_crash_df._df_from_online_requests())
   # pass
   # updated_df = df_loaded_with_auto_update(CRASH_CSV)
   # if updated_df is not None:
   #    print(updated_df.head())
   #    print(updated_df.tail())
   #    print()
   #    print("(New updated entries will not be saved to local files for demonstrating this update feature.)")
   # else:
   #    pass
   # print("-"*100)
   # print("TEST FOR SUPERCLASS FUNCTION df_head")
   # mtcars_raw = pd_crash.read_csv("https://raw.githubusercontent.com/selva86/datasets/master/mtcars.csv")
   # mtcars_df = CrashDf(mtcars_raw)
   # # method from super class DSDf
   # mtcars_df.df_head()
   # print("-"*100)
   # print("TEST FOR GEOMETRY WRANGLING")
   # bound_dict = CrashDf.crash_geometry_wrangling()
   # print(bound_dict.get('x_bounds')[0])
   # print(bound_dict.get('x_bounds')[1])
   # print(bound_dict.get('y_bounds')[0])
   # print(bound_dict.get('y_bounds')[1])
   # print("-"*100)
