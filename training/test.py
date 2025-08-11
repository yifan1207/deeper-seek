# # import ee
# # import pandas as pd
# # from pandarallel import pandarallel

# # ee.Initialize(project="first-vision-443700-p2")


# # pandarallel.initialize(nb_workers=16, progress_bar=True)

# # df = pd.read_csv("./training/pathlatlon.csv")

# # year = 2024
# # emb_img = ee.ImageCollection("GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL").filterDate(f"{year}-01-01", f"{year + 1}-01-01").mosaic().toArray()


# # def get_embedding(row):
# #     global valid
# # #     lon = row["longitude"]
# # #     lat = row["latitude"]
# # #     point = ee.Geometry.Point([lon, lat])
# # #     emb_arr = emb_img.reduceRegion(reducer=ee.Reducer.first(), geometry=point, scale=10, maxPixels=1e9).get("array")

# # #     if emb_arr:
# # #         emb_list = ee.Array(emb_arr).toList().getInfo()
# # #         return emb_list
# # #     else:
# # #         return None


# # # print("starting")
# # # df["embedding"] = df.parallel_apply(get_embedding, axis=1)

# # # df.to_csv("path_lat_lon_with_embeddings.csv", index=False)


# # import ee
# # import polars as pl

# # ee.Initialize(project="first-vision-443700-p2")


# # df = pl.read_csv("./training/pathlatlon.csv")


# # # Create a FeatureCollection from points
# # points = [ee.Feature(ee.Geometry.Point([row[2], row[3]])) for row in df.iter_rows()]
# # feature_collection = ee.FeatureCollection(points)


# # print("made feature collection")
# # year = 2024
# # emb_img = ee.ImageCollection("GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL").filterDate(f"{year}-01-01", f"{year + 1}-01-01").mosaic().toArray()
# # print("embedding")
# # # Perform reduceRegions: get 'array' property for all points in one request
# # result = emb_img.reduceRegions(
# #     collection=feature_collection,
# #     reducer=ee.Reducer.first(),
# #     scale=10,
# #     tileScale=4,  # Adjust based on memory and performance
# # )
# # print("reduced regions")
# # # Get the results as a list of dictionaries (this pulls data into Python)
# # features_info = result.getInfo()["features"]

# # print("extracting embeddings")
# # embeddings = []
# # for f in features_info:
# #     emb = f["properties"].get("array")
# #     embeddings.append(emb)

# # df["embedding"] = embeddings

# # df.to_csv("path_lat_lon_with_embeddings.csv", index=False)

# import ee
# import polars as pl

# ee.Initialize(project="first-vision-443700-p2")

# df = pl.read_csv("./training/pathlatlon.csv")

# # Create a FeatureCollection from points with unique IDs
# features = []
# for i, row in enumerate(df.iter_rows()):
#     point = ee.Feature(ee.Geometry.Point([row[2], row[3]]), {"point_id": i})
#     features.append(point)

# feature_collection = ee.FeatureCollection(features)

# year = 2024
# emb_img = ee.ImageCollection("GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL").filterDate(f"{year}-01-01", f"{year + 1}-01-01").mosaic().toArray()

# # Perform reduceRegions
# result = emb_img.reduceRegions(collection=feature_collection, reducer=ee.Reducer.first(), scale=10, tileScale=4)

# # Export instead of getInfo()
# task = ee.batch.Export.table.toDrive(
#     collection=result,
#     description="embeddings_export",
#     fileFormat="CSV",
#     selectors=["point_id", "array"],  # Only export needed properties
# )
# task.start()

# print("Export started. Check Google Drive for results.")


import os
import time
import pandas as pd
import ee
from pandarallel import pandarallel

pandarallel.initialize(nb_workers=16, progress_bar=True)  # fewer workers to reduce 429s

SRC = "./training/pathlatlon.csv"
OUT = "./path_lat_lon_with_embeddings.csv"
ee.Initialize(project="first-vision-443700-p2")
df = pd.read_csv(SRC)

year = 2024
emb_img = ee.ImageCollection("GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL").filterDate(f"{year}-01-01", f"{year + 1}-01-01").mosaic().toArray()


def get_embedding(row):
    lon = row["longitude"]
    lat = row["latitude"]
    point = ee.Geometry.Point([lon, lat])
    try:
        emb_arr = emb_img.reduceRegion(reducer=ee.Reducer.first(), geometry=point, scale=10, maxPixels=1e9).get("array")
        if emb_arr:
            return ee.Array(emb_arr).toList().getInfo()
    except Exception:
        return None
    return None


batch_size = 2048
for start in range(0, len(df), batch_size):
    batch = df.iloc[start : start + batch_size].copy()
    batch["embedding"] = batch.parallel_apply(get_embedding, axis=1)

    header = not os.path.exists(OUT)
    batch.to_csv(OUT, mode="a", header=header, index=False)
    time.sleep(1)
