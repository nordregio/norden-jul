from flask import Flask, send_from_directory
import pandas as pd
import geopandas as gpd
from shapely import wkb
import ast
import json

# MUNICIPAL BORDERS LAYER
with open("data/nordic_polygons_flat.txt", "r") as file:
    content = file.read()

borders = ast.literal_eval(content.split("= ")[1])

# POPULATION GRID LAYER
DATA = "data/nordic_points.geoparquet"
df = pd.read_parquet(DATA)
df["geometry"] = df["geometry"].apply(wkb.loads)
df = gpd.GeoDataFrame(df, geometry="geometry")
df["lng"] = df["geometry"].x
df["lat"] = df["geometry"].y

df = df[
    [
        "lat",
        "lng",
        "population",
        "munname",
    ]
]


def assign_color(population):
    if population < 5:
        return [189, 214, 196, 255]  # #BDD6C4
    elif population < 15:
        return [169, 200, 175, 255]  # #A9C8AF
    elif population < 50:
        return [149, 187, 152, 255]  # #95BB98
    elif population < 100:
        return [131, 172, 130, 255]  # #83AC82
    elif population < 200:
        return [118, 158, 111, 255]  # #769E6F
    elif population < 1000:
        return [105, 143, 92, 255]  # #698F5C
    elif population < 4000:
        return [93, 133, 83, 255]  # #5D8553
    elif population < 6000:
        return [195, 110, 81, 255]  # #C36E51
    elif population < 10000:
        return [166, 75, 62, 255]  # #A64B3E
    else:
        return [125, 44, 44, 255]  # #7D2C2C


df["fill_color"] = df["population"].apply(assign_color)

app = Flask(__name__)


@app.route("/save")
def save():
    with open("layers/polygon_layer.json", "w") as h:
        h.write(json.dumps(borders))

    with open("layers/column_layer.json", "w") as h:
        h.write(df.to_json(orient="records"))

    return "done"

    # index.html was generated with pydeck before

    # with open("index.html", "w") as h:
    #     h.write(html)


@app.route("/layers/<path:name>")
def serve_layers(name):
    return send_from_directory("layers", name)


@app.route("/")
def index():
    with open("index.html", "r") as h:
        return h.read()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, use_reloader=True, debug=True)
