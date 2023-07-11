import pandas as pd
import geopandas
from geopandas import GeoDataFrame
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from itertools import permutations
import matplotlib.pyplot as plt
from shapely.ops import nearest_points
from shapely.geometry import Point
import pyproj

# button = tk.Button(master=root, text="Erstellen", command=_firstPlot)
# button.pack(side=tk.BOTTOM)
# button = tk.Button(master=root, text="Verlassen", command=_quit)
# button.pack(side=tk.BOTTOM)
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

# Krimi Daten aufbereiten
dfKrimi["Straftaten -insgesamt-"] = dfKrimi["Straftaten -insgesamt-"].str.replace(
    ".", ""
)

dfKrimi["Straftaten -insgesamt-"] = (
    pd.to_numeric(dfKrimi["Straftaten -insgesamt-"], errors="coerce")
    .fillna(0)
    .astype(float)
)
dfKrimiWithLOR = pd.merge(
    dfKrimi,
    data_bzr,
    left_on="LOR-Schlüssel (Bezirksregion)",
    right_on="BZR_ID",
)
gdfKrimiWithLOR = GeoDataFrame(dfKrimiWithLOR, crs="EPSG:25833", geometry="geometry")

gdfGewerbe = geopandas.GeoDataFrame(
    dfGewerbe,
    geometry=geopandas.points_from_xy(dfGewerbe["longitude"], dfGewerbe["latitude"]),
    crs="ETRS89",
)
gdfGewerbe = gdfGewerbe.to_crs(epsg=25833)

train_stations_df = pd.DataFrame(train_stations)

train_stations_gdf = geopandas.GeoDataFrame(
    train_stations_df,
    geometry=geopandas.points_from_xy(
        train_stations_df["Longitude"], train_stations_df["Latitude"]
    ),
    crs="ETRS89",
)
train_stations_gdf = train_stations_gdf.to_crs(epsg=25833)

gdfKitas = geopandas.GeoDataFrame(
    dfKitas,
    geometry=geopandas.points_from_xy(dfKitas["lon"], dfKitas["lat"]),
    crs="ETRS89",
)


gdfKitas = gdfKitas.to_crs(epsg=25833)

# Create the tkinter window
window = tk.Tk()
window.title("IHK-Projekt Gruppe NOLL")
window.state("zoomed")

fig, ax = plt.subplots(figsize=(4, 3))

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Create the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas, window)
toolbar.pack(side=tk.BOTTOM, fill=tk.X)

# Create a frame with a scrollbar for the dropdowns
frame = tk.Frame(window)
frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

dropdown_frame = tk.Canvas(frame, yscrollcommand=scrollbar.set)
dropdown_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=dropdown_frame.yview)

# Generate all possible color combinations
colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]
color_combinations = list(permutations(colors, 3))

legends = {
    "filteredGewerbe": "Gewerbe",
    "gdfKitas": "Kitas",
    "train_stations_gdf": "Bahnhöfe",
}

trv = ttk.Treeview(window, selectmode="browse")
trv.pack()


def calculateScore(impKitas, impIHK, impBahnhof, impKrimi, branche):
    gdfKrimiWithLOR = geopandas.GeoDataFrame(dfKrimiWithLOR, geometry="geometry")
    gdfKrimiWithLOR["Zentren"] = gdfKrimiWithLOR["geometry"].centroid
    data_bzr["Zentren"] = data_bzr["geometry"].centroid

    result_df = geopandas.GeoDataFrame(
        columns=[
            "Bezirksregion",
            "Bezirk_ID",
            "Nearest_Station",
            "Station_Name",
            "Distance",
        ]
    )

    for index, row in data_bzr.iterrows():
        centroid = row["Zentren"]
        bezirksregion = row["BZR_NAME"]
        bezirksregion_id = row["BZR_ID"]
        # bezirksregion_geometry = row["geometry"]

        # Calculate the nearest station and distance
        nearest_station = nearest_points(centroid, train_stations_gdf.unary_union)[1]
        distance = distance = centroid.distance(nearest_station) / 1000
        nearest_station_name = nearest_station_name = train_stations_gdf.loc[
            train_stations_gdf["geometry"] == nearest_station, "Train Station"
        ].values[0]

        result_df.loc[index] = [
            bezirksregion,
            bezirksregion_id,
            nearest_station,
            nearest_station_name,
            distance,
        ]

    dfBezirke = pd.DataFrame()
    dfBezirke["Bezirksregion"] = data_bzr["BZR_NAME"]
    dfBezirke["Bezirk_ID"] = data_bzr["BZR_ID"]

    gdfKitas = geopandas.GeoDataFrame(
        dfKitas,
        geometry=geopandas.points_from_xy(dfKitas["lon"], dfKitas["lat"]),
        crs="ETRS89",
    )

    gdfKitas = gdfKitas.to_crs(epsg=25833)

    gdfKitas["unique_id"] = gdfKitas.index

    # Create an empty column 'Bezirksregion' in dfKitas
    gdfKitas["Bezirksregion"] = ""
    gdfKitas["Bezirk_ID"] = ""

    # Iterate over each row in dfKitas
    for indexKita, kita in gdfKitas.iterrows():
        # Iterate over each row in data_bzr
        for index, bzr in data_bzr.iterrows():
            # Check if the point is within the polygon
            if kita["geometry"].within(bzr["geometry"]):
                # Assign the Bezirksregion value to dfKitas
                gdfKitas.at[indexKita, "Bezirksregion"] = bzr["BZR_NAME"]
                gdfKitas.at[indexKita, "Bezirk_ID"] = bzr["BZR_ID"]
                break  # Exit the inner loop if a match is found

    # merge Kita-Counts in dfBezirke
    merged_df = dfBezirke.merge(
        gdfKitas.groupby("Bezirk_ID")["unique_id"].count(),
        on="Bezirk_ID",
        how="left",
    )
    merged_df = merged_df.rename(columns={"unique_id": "Kitas in Bezirksregion"})
    # merge die Krimi-Daten mit rein
    merged_df2 = pd.merge(
        dfKrimi,
        merged_df,
        left_on="LOR-Schlüssel (Bezirksregion)",
        right_on="Bezirk_ID",
    )
    merged_df2 = merged_df2[
        [
            "Bezirksregion",
            "Bezirk_ID",
            "Kitas in Bezirksregion",
            "Straftaten -insgesamt-",
        ]
    ]

    result_gdf = geopandas.GeoDataFrame(
        result_df, geometry="Nearest_Station", crs="epsg:25833"
    )

    # filtere ggf. die Gewerbedaten
    # merge die Gewerbedaten mit rein
    dfGewerbe["Bezirk_ID"] = dfGewerbe["planungsraum_id"].str.strip("'").str[:6]

    if branche != "":
        filtered_df = dfGewerbe[dfGewerbe["ihk_branch_desc"] == branche]
        merged_df3 = pd.merge(
            filtered_df.groupby(["Bezirk_ID"])["opendata_id"]
            .count()
            .reindex(
                dfGewerbe["Bezirk_ID"].unique(), fill_value=0
            ),  # filtered_df.groupby(["Bezirk_ID"])["opendata_id"].count(),
            merged_df2,
            left_on="Bezirk_ID",
            right_on="Bezirk_ID",
        )
    # if branche != "":
    #     filtered_df = dfGewerbe[dfGewerbe["nace_desc"] == branche]

    #     merged_df3 = pd.merge(
    #         filtered_df.groupby(["Bezirk_ID"])["opendata_id"]
    #         .count()
    #         .reindex(
    #             dfGewerbe["Bezirk_ID"].unique(), fill_value=0
    #         ),  # filtered_df.groupby(["Bezirk_ID"])["opendata_id"].count(),
    #         merged_df2,
    #         left_on="Bezirk_ID",
    #         right_on="Bezirk_ID",
    #     )
    else:
        merged_df3 = pd.merge(
            dfGewerbe.groupby(["Bezirk_ID"])["opendata_id"].count(),
            merged_df2,
            left_on="Bezirk_ID",
            right_on="Bezirk_ID",
        )

    merged_df3 = merged_df3.rename(columns={"opendata_id": "Gewerbe in Bezirksregion"})

    merged_df4 = pd.merge(
        merged_df3,
        result_gdf[["Bezirk_ID", "Station_Name", "Distance"]],
        on="Bezirk_ID",
        how="left",
    )
    merged_df4 = merged_df4.rename(
        columns={"Station_Name": "Naechster Bahnhof", "Distance": "Distanz"}
    )

    merged_df4["Score"] = round(
        (
            (
                int(impKrimi)
                * (-1)
                * (
                    100
                    * (
                        (merged_df4["Straftaten -insgesamt-"].astype(int) - 0)
                        / (merged_df4["Straftaten -insgesamt-"].max().astype(int) - 0)
                    )
                )
            )
            + (
                int(impIHK)
                * (1)
                * (
                    100
                    * (
                        (merged_df4["Gewerbe in Bezirksregion"].astype(int) - 0)
                        / (merged_df4["Gewerbe in Bezirksregion"].max().astype(int) - 0)
                    )
                )
            )
            + (
                int(impKitas)
                * (1)
                * (
                    100
                    * (
                        (merged_df4["Kitas in Bezirksregion"].astype(int) - 0)
                        / (merged_df4["Kitas in Bezirksregion"].max().astype(int) - 0)
                    )
                )
            )
            + (
                int(impBahnhof)
                * (-1)
                * (
                    100
                    * (
                        (merged_df4["Distanz"].astype(int) - 0)
                        / (merged_df4["Distanz"].max().astype(int) - 0)
                    )
                )
            )
        ),
        2,
    )

    merged_df4["Score"] = round(
        (100 * (merged_df4["Score"] - (-2000)) / (2000 - (-2000))), 2
    )
    # Score berechnen
    # merged_df4["Score"] = round(
    #     (
    #         merged_df4["Straftaten -insgesamt-"].max().astype(int)
    #         / merged_df4["Gewerbe in Bezirksregion"].max().astype(int)
    #     )
    #     * (-1)
    #     * (merged_df4["Gewerbe in Bezirksregion"].astype(int) * int(impIHK))
    #     + (
    #         merged_df4["Straftaten -insgesamt-"].max().astype(int)
    #         / merged_df4["Distanz"].max().astype(int)
    #     )
    #     * (-1)
    #     * (merged_df4["Distanz"].astype(float) * int(impBahnhof))
    #     + (
    #         merged_df4["Straftaten -insgesamt-"].max().astype(int)
    #         / merged_df4["Kitas in Bezirksregion"].max().astype(int)
    #     )
    #     + (merged_df4["Kitas in Bezirksregion"].astype(int) * int(impKitas))
    #     * (-1)
    #     * (merged_df4["Straftaten -insgesamt-"].astype(int) * int(impKrimi)),
    #     2,
    # )

    merged_df4["Distanz"] = round(merged_df4["Distanz"], 3)
    # merged_df4["Straftaten -insgesamt-"] = int(merged_df4["Straftaten -insgesamt-"])

    # merged_df4 = merged_df4.sort_values(by="Score", ascending=False)
    merged_df4 = merged_df4.sort_values(by="Score", ascending=False)

    # Define the columns of the treeview
    trv["columns"] = (
        "Bezirksregion",
        "Gewerbe in Bezirksregion",
        "Distanz",
        "Naechster Bahnhof",
        "Kitas in Bezirksregion",
        "Straftaten -insgesamt-",
        "Score",
    )
    # trv.heading("#0", text="")  # Empty heading for the first column
    trv.heading("Bezirksregion", text="Bezirksregion")
    trv.heading("Gewerbe in Bezirksregion", text="Anz. d Gewerbe in Bezirksregion")
    trv.heading("Distanz", text="Distanz zum naechsten Bahnhof in Km")
    trv.heading("Naechster Bahnhof", text="Naechster Bahnhof")
    trv.heading("Kitas in Bezirksregion", text="Kitas in Bezirksregion")
    trv.heading("Straftaten -insgesamt-", text="Straftaten -insgesamt-")
    trv.heading("Score", text="Score")

    for child in trv.get_children():
        trv.delete(child)

    window.update_idletasks()

    for index, row in merged_df4.iterrows():
        trv.insert(
            parent="",
            index="end",
            iid=index,
            values=(
                row["Bezirksregion"],
                row["Gewerbe in Bezirksregion"],
                row["Distanz"],
                row["Naechster Bahnhof"],
                row["Kitas in Bezirksregion"],
                row["Straftaten -insgesamt-"],
                row["Score"],
            ),
        )


def update_figure(event=None):
    ax.clear()
    ax.set_axis_off()

    # Get the values from the sliders and dropdown
    slider1_value = dropdown1.get()
    slider2_value = dropdown2.get()
    slider3_value = dropdown3.get()
    slider4_value = dropdown4.get()
    dropdown_value = dropdown.get()

    # Get the selected color combination
    selected_colors = color_dropdown.get().split(",")
    selected_colors = selected_colors[0].split()

    color1, color2, color3 = (
        selected_colors if len(selected_colors) == 3 else ["green", "red", "blue"]
    )

    edgecolor = "black"
    slider1_marker = int(slider1_value) if int(slider1_value) else 0
    slider2_marker = int(slider2_value) if int(slider2_value) else 0
    slider3_marker = int(slider3_value) if int(slider3_value) else 0
    filteredGewerbe = (
        gdfGewerbe[gdfGewerbe["ihk_branch_desc"] == dropdown_value]
        if dropdown_value
        else gdfGewerbe
    )
    # Test with Nace_desc instead of ihk_branch
    # filteredGewerbe = (
    #     gdfGewerbe[gdfGewerbe["nace_desc"] == dropdown_value]
    #     if dropdown_value
    #     else gdfGewerbe
    # )

    # Iterate over each row in dfKitas
    for indexKita, kita in gdfKitas.iterrows():
        # Iterate over each row in data_bzr
        for index, bzr in data_bzr.iterrows():
            # Check if the point is within the polygon
            if kita["geometry"].within(bzr["geometry"]):
                # Assign the Bezirksregion value to dfKitas
                gdfKitas.at[indexKita, "Bezirksregion"] = bzr["BZR_NAME"]
                gdfKitas.at[indexKita, "Bezirk_ID"] = bzr["BZR_ID"]
                break  # Exit the inner loop if a match is found

    # Filter die Kitas, die ebenfalls in den Regionen der angezeigten Unternehmen liegen
    filteredKitas = (
        gdfKitas[gdfKitas["Bezirksregion"].isin(filteredGewerbe["Bezirksregion"])]
        if dropdown_value
        else gdfKitas
    )

    alphaGewerbe = 1 if dropdown_value else 0.1

    # data_bzr.geometry.boundary.plot(color=None,edgecolor='red',linewidth = 1,ax=ax)
    # data_plr.geometry.boundary.plot(color=None,edgecolor='black',linewidth = 1,ax=ax)
    # data_straßennetz.plot(color=None,edgecolor='grey',linewidth = 0.2,ax=ax)
    # data_pgr.geometry.boundary.plot(color=None, edgecolor="black", linewidth=1, ax=ax)

    # Plot the combined GeoDataFrame

    gdfKrimiWithLOR.plot(
        column="Straftaten -insgesamt-",
        cmap="YlOrRd",
        linewidth=0.3,
        edgecolor=edgecolor,
        ax=ax,
    )
    filteredGewerbe.plot(
        markersize=(slider2_marker + 1) / 3,
        color=color1,
        ax=ax,
        label=legends["filteredGewerbe"],
        alpha=alphaGewerbe,
    )

    # gdfKitas.plot(
    #     markersize=(slider1_marker + 1) / 5,
    #     color=color2,
    #     ax=ax,
    #     marker="s",
    #     label=legends["gdfKitas"],
    # )
    filteredKitas.plot(
        markersize=(slider1_marker + 1) / 8,
        color=color2,
        ax=ax,
        marker="s",
        label=legends["gdfKitas"],
    )

    train_stations_gdf.plot(
        markersize=(slider3_marker + 1) / 2,
        color=color3,
        ax=ax,
        label=legends["train_stations_gdf"],
    )

    plt.tight_layout()
    # Add legend to the plot
    legend = ax.legend(loc="lower left", prop={"size": 5})

    # Set marker sizes in the legend
    for lh in legend.legend_handles:
        lh._sizes = [30]
    # Re-render the matplotlib figure
    calculateScore(
        slider1_value, slider2_value, slider3_value, slider4_value, dropdown_value
    )
    canvas.draw()


# Create a new dropdown for color combinations
color_dropdown_label = tk.Label(dropdown_frame, text="Farbauswahl")
color_dropdown_label.grid(row=0, column=0, sticky="w")
color_dropdown = ttk.Combobox(dropdown_frame, values=color_combinations)
color_dropdown.grid(row=0, column=1, sticky="w")
color_dropdown.bind("<<ComboboxSelected>>", update_figure)
# Set default value for the color dropdown
color_dropdown.set(color_combinations[0])

dropdown_label1 = tk.Label(dropdown_frame, text="Kitas")
dropdown_label1.grid(row=1, column=0, sticky="w")
dropdown1 = ttk.Combobox(dropdown_frame, values=list(range(11)))
dropdown1.set("0")
dropdown1.grid(row=1, column=1, sticky="w")
dropdown1.bind("<<ComboboxSelected>>", update_figure)

dropdown_label2 = tk.Label(dropdown_frame, text="Gewerbe")
dropdown_label2.grid(row=1, column=2, sticky="w")
dropdown2 = ttk.Combobox(dropdown_frame, values=list(range(11)))
dropdown2.set("0")
dropdown2.grid(row=1, column=3, sticky="w")
dropdown2.bind("<<ComboboxSelected>>", update_figure)

dropdown_label3 = tk.Label(dropdown_frame, text="Bahnhöfe")
dropdown_label3.grid(row=2, column=0, sticky="w")
dropdown3 = ttk.Combobox(dropdown_frame, values=list(range(11)))
dropdown3.set("0")
dropdown3.grid(row=2, column=1, sticky="w")
dropdown3.bind("<<ComboboxSelected>>", update_figure)

dropdown_label4 = tk.Label(dropdown_frame, text="Kriminalität")
dropdown_label4.grid(row=1, column=4, sticky="w")
dropdown4 = ttk.Combobox(dropdown_frame, values=list(range(11)))
dropdown4.set("0")
dropdown4.grid(row=1, column=5, sticky="w")
dropdown4.bind("<<ComboboxSelected>>", update_figure)

#
dropdown_label = tk.Label(dropdown_frame, text="Branche")
dropdown_label.grid(row=2, column=2, sticky="w")
dropdown_values = sorted(
    dfGewerbe["ihk_branch_desc"].dropna().unique().astype(str).tolist()
)
dropdown = ttk.Combobox(dropdown_frame, values=dropdown_values)
dropdown.grid(row=2, column=3, sticky="w")
dropdown.bind("<<ComboboxSelected>>", update_figure)

# dropdown_label = tk.Label(dropdown_frame, text="Branche (NACE)")
# dropdown_label.grid(row=2, column=2, sticky="w")
# dropdown_values = sorted(dfGewerbe["nace_desc"].dropna().unique().astype(str).tolist())
# dropdown = ttk.Combobox(dropdown_frame, values=dropdown_values)
# dropdown.grid(row=2, column=3, sticky="w")
# dropdown.bind("<<ComboboxSelected>>", update_figure)

# calculateScore(slider1_value, slider2_value, slider3_value, slider4_value, dropdown_value)

update_figure()

window.mainloop()
