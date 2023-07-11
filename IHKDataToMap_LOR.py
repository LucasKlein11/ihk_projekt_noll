import pandas as pd
import geopandas
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from tkinter import ttk
import tkinter as tk

# Dateipfade der shp-Dateien
fp_bzr = "lor_bzr.shp"
fp_bzr = "lor_bzr.shp"
fp_pgr = "lor_pgr.shp"
fp_plr = "lor_plr.shp"
straßennetz = "Detailnetz-Strassenabschnitte.shp"
fp_pgr = "lor_pgr.shp"

# Laden der Gewerbedaten
dfGewerbe = pd.read_csv("IHKBerlin_Gewerbedaten.csv", sep=",")
# Laden der Zugstationen
train_stations = pd.read_json("train_stations.json")
# Laden der Bezirksregionen
data_bzr = geopandas.read_file(fp_bzr)
# Lesen der PGR-Daten
data_pgr = geopandas.read_file(fp_pgr)
# Laden der Planungsräume
data_plr = geopandas.read_file(fp_plr)
# Laden des Straßennetzes
data_straßennetz = geopandas.read_file(straßennetz)
# Laden der Fallzahlen
dfKrimi = pd.read_csv(
    "Fallzahlen&HZ 2013-2022.csv",
    delimiter=";",
    dtype={"LOR-Schlüssel (Bezirksregion)": str},
)
# Kitas laden
dfKitas = pd.read_csv("berlin_kitas.csv", delimiter=";")  # error_bad_lines=False

main_window = tk.Tk()
main_window.config(width=300, height=200)
main_window.title("Branche wählen")
combo = ttk.Combobox(values=dfGewerbe["ihk_branch_desc"].unique().tolist())
combo.place(x=50, y=50)

init_kita = 0
init_krimi = 0
init_gleicheBranche = 0


markerSizeKita = input("Wie wichtig sind dir Kitas?")
markerSizeGewerbe = input("Wie wichtig sind dir Kitas?")


# Krimi Daten aufbereiten

dfKrimi["Straftaten -insgesamt-"] = dfKrimi["Straftaten -insgesamt-"].str.replace(
    ".", ""
)
dfKrimi["Straftaten -insgesamt-"] = (
    pd.to_numeric(dfKrimi["Straftaten -insgesamt-"], errors="coerce")
    .fillna(0)
    .astype(float)
)

dfKrimiWithGeoData = pd.merge(
    dfKrimi, data_bzr, left_on="LOR-Schlüssel (Bezirksregion)", right_on="BZR_ID"
)
gdfKrimiWithGeoData = GeoDataFrame(
    dfKrimiWithGeoData, crs="EPSG:25833", geometry="geometry"
)

# Bahnhöfe aufbereiten

train_stations_df = pd.DataFrame(train_stations)

train_stations_gdf = geopandas.GeoDataFrame(
    train_stations_df,
    geometry=geopandas.points_from_xy(
        train_stations_df["Longitude"], train_stations_df["Latitude"]
    ),
    crs="ETRS89",
)

# Gewerbedaten aufbereiten

gdfGewerbe = geopandas.GeoDataFrame(
    dfGewerbe,
    geometry=geopandas.points_from_xy(dfGewerbe["longitude"], dfGewerbe["latitude"]),
    crs="ETRS89",
)

# Ist das nötig?
# data_etrs89_Gewerbe = gdfGewerbe.copy()
# data_etrs89_Bahnhof = train_stations_gdf.copy()

# Transformiere zu anderem CRS (hier zu CRS, die daten.berlin.de nutzt)
gdfGewerbe = gdfGewerbe.to_crs(epsg=25833)
train_stations_gdf = train_stations_gdf.to_crs(epsg=25833)


gdfKitas = geopandas.GeoDataFrame(
    dfKitas,
    geometry=geopandas.points_from_xy(dfKitas["lon"], dfKitas["lat"]),
    crs="ETRS89",
)
#
# data_etrs89 = gdf.copy()

gdfKitas = gdfKitas.to_crs(epsg=25833)


fig, ax = plt.subplots(figsize=(10, 10))
ax.set_axis_off()

fig.subplots_adjust(left=0.25, bottom=0.25)
# Vertikale Achse
# axamp = fig.add_axes([0.1, 0.3, 0.0225, 0.63])
# kita_slider = Slider(
#     ax=axamp,
#     label="Wichtigkeit der Nähe zur Kita",
#     valmin=0,
#     valmax=10,
#     valinit=init_kita,
#     orientation="vertical",
# )

# # Horizontale Achse 2
# axfreq = fig.add_axes([0.25, 0.2, 0.65, 0.03])
# branche_slider = Slider(
#     ax=axfreq,
#     label="Wichtigkeit Firmen gleicher Branche",
#     valmin=0,
#     valmax=10,
#     valinit=init_krimi,
# )

# def updateKita(val):
#     print(val)
#     markerSizeKita = val
#     gdfKitas.plot(markersize=markerSizeKita, color="green", ax=ax, marker="s")
#     fig.canvas.draw_idle()

# def updateGewerbe(val):
#     print(val)
#     markerSizeGewerbe = val
#     gdfGewerbe.plot(markersize=markerSizeGewerbe / 100, color="blue", ax=ax)
#     fig.canvas.draw_idle()

# # register the update function with each slider
# kita_slider.on_changed(updateKita)
# branche_slider.on_changed(updateGewerbe)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
# resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
# button = Button(resetax, "Reset", hovercolor="0.975")

# def reset(event):
#     kita_slider.reset()
#     branche_slider.reset()

# button.on_clicked(reset)

# data_bzr.geometry.boundary.plot(color=None,edgecolor='red',linewidth = 1,ax=ax)
# Plotte die Planungsräume mit schwarzen Linien
# data_plr.geometry.boundary.plot(color=None,edgecolor='black',linewidth = 1,ax=ax)
# data_straßennetz.plot(color=None,edgecolor='grey',linewidth = 0.2,ax=ax)
# data_pgr.geometry.boundary.plot(color=None, edgecolor="black", linewidth=1, ax=ax)

# gdfKrimiWithGeoData.plot(
#     column="Straftaten -insgesamt-",
#     cmap="BuPu",
#     linewidth=0.5,
#     ax=ax,
#     edgecolor="black",
# )
# gdfGewerbe.plot(markersize=(markerSizeGewerbe / 100), color="blue", ax=ax)
# gdfKitas.plot(markersize=markerSizeKita, color="green", ax=ax, marker="s")

# # plt.tight_layout()
# plt.show()
