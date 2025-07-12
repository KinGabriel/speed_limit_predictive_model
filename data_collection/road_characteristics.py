import requests
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling
import rasterio.features
from geopy.geocoders import Nominatim
import time

# === Load and fix DEM ===
dem_path = "cut_n00e120.tif"
with rasterio.open(dem_path) as dem_src:
    dem_crs = dem_src.crs or "EPSG:4326"
    dem_data = dem_src.read(1).astype(float)
    dem_data[dem_data == -32768] = np.nan
    dem_bounds = dem_src.bounds
    dem_transform = dem_src.transform
    dem_meta = dem_src.meta

# === Reproject DEM to UTM Zone 51N ===
dst_crs = "EPSG:32651"
scale = 0.5
transform, width, height = calculate_default_transform(
    dem_crs, dst_crs, dem_data.shape[1], dem_data.shape[0], *dem_bounds
)
width = int(width * scale)
height = int(height * scale)

kwargs = dem_meta.copy()
kwargs.update({"crs": dst_crs, "transform": transform, "width": width, "height": height})

memfile = rasterio.io.MemoryFile()
with memfile.open(**kwargs) as dst:
    reproject(
        source=dem_data,
        destination=rasterio.band(dst, 1),
        src_transform=dem_transform,
        src_crs=dem_crs,
        dst_transform=transform,
        dst_crs=dst_crs,
        resampling=Resampling.bilinear
    )
    reprojected_dem = dst.read(1)
    reprojected_transform = dst.transform

# === Helper functions ===
def compute_mean_curvature(line):
    coords = np.array(line.coords)
    if len(coords) < 3: return 0
    angles = []
    for i in range(1, len(coords)-1):
        v1, v2 = coords[i] - coords[i-1], coords[i+1] - coords[i]
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 == 0 or n2 == 0: continue
        angle = np.arccos(np.clip(np.dot(v1, v2)/(n1*n2), -1, 1))
        angles.append(angle)
    mean_angle = np.mean(angles) if angles else 0
    mean_seg = np.mean([np.linalg.norm(coords[i+1]-coords[i]) for i in range(len(coords)-1)])
    return (mean_angle / mean_seg) if mean_seg else 0

def get_bbox_from_city(city_name):
    geolocator = Nominatim(user_agent="osm_city_locator")
    for _ in range(3):
        try:
            loc = geolocator.geocode(city_name + ", Philippines")
            if loc and 'boundingbox' in loc.raw:
                south, north, west, east = map(float, loc.raw['boundingbox'])
                return city_name, (west, south, east, north)
        except:
            time.sleep(1)
    return None

# === City names ===
city_names = [
    "Baguio", "Tabuk", "Dagupan", "San Carlos", "Santiago", "Ilagan", "SJDM", "Tarlac",
    "Antipolo", "Dasma", "Puerto Princesa", "Naujan", "Naga", "Sorsogon", "Bacolod", "Iloilo",
    "Cebu", "Barili", "Tacloban", "Ormoc", "Zamboanga", "Sindangan", "CDO", "Gingoog",
    "Davao", "Samal", "GenSan", "Palimbang", "Butuan", "Bayugan", "Cotabato", "Marawi",
    "Quezon City"
]

city_boxes = [get_bbox_from_city(name) for name in city_names if get_bbox_from_city(name)]

# === Fetch roads ===
overpass_url = "http://overpass-api.de/api/interpreter"
all_records = []

for city, (minx, miny, maxx, maxy) in city_boxes:
    query = f"""
    [out:json][timeout:25];
    (
      way["highway"]({miny},{minx},{maxy},{maxx});
    );
    out geom;
    """
    try:
        response = requests.get(overpass_url, params={'data': query})
        elements = response.json().get("elements", [])
    except Exception:
        continue

    for elem in elements:
        tags = elem.get("tags", {})
        highway = tags.get("highway")
        if highway not in ["primary", "secondary", "tertiary","residential","trunk"]:
            continue
        line = LineString([(pt['lon'], pt['lat']) for pt in elem['geometry']])
        all_records.append({
            "city": city,
            "osm_id": elem['id'],
            "name": tags.get("name"),
            "highway": highway,
            "lanes": tags.get("lanes"),
            "maxspeed": tags.get("maxspeed"),
            "surface": tags.get("surface"),
            "bridge": int("bridge" in tags),
            "tunnel": int("tunnel" in tags),
            "lit": int("lit" in tags),
            "sidewalk": int("sidewalk" in tags),
            "oneway": int("oneway" in tags),
            "cycleway": int("cycleway" in tags),
            "geometry": line
        })

# === GeoDataFrame and features ===
gdf = gpd.GeoDataFrame(all_records, geometry="geometry", crs="EPSG:4326").to_crs(dst_crs)
gdf["original_line"] = gdf.geometry

slopes, lengths, curvatures, widths = [], [], [], []

for idx, row in gdf.iterrows():
    line = row.original_line
    lengths.append(line.length)
    curvatures.append(compute_mean_curvature(line))
    poly = line.buffer(10)
    widths.append(poly.area / line.length if line.length else 0)

    try:
        window = from_bounds(*poly.bounds, transform=reprojected_transform)
        r1, r2 = int(window.row_off), int(window.row_off + window.height)
        c1, c2 = int(window.col_off), int(window.col_off + window.width)
        dem_slice = reprojected_dem[r1:r2, c1:c2]
        if dem_slice.shape[0] < 3 or dem_slice.shape[1] < 3:
            slopes.append(None)
            continue
        small_transform = rasterio.transform.from_origin(
            reprojected_transform.c + c1 * reprojected_transform.a,
            reprojected_transform.f + r1 * reprojected_transform.e,
            reprojected_transform.a,
            -reprojected_transform.e
        )
        slope_array = compute_slope(dem_slice, small_transform)
        mask = rasterio.features.geometry_mask([poly], slope_array.shape, small_transform, invert=True)
        valid = mask & (~np.isnan(slope_array))
        slopes.append(slope_array[valid].mean() if np.any(valid) else None)
    except Exception:
        slopes.append(None)

# === Assign results ===
gdf["segment_length"] = lengths
gdf["segment_width"] = widths
gdf["mean_curvature"] = curvatures

gdf["surface"] = gdf["surface"].fillna(gdf["surface"].mode().iloc[0] if not gdf["surface"].mode().empty else "asphalt")
gdf["lanes"] = gdf["lanes"].fillna(2)
gdf["maxspeed"] = gdf.apply(
    lambda row: row["maxspeed"] or {"primary": "80", "secondary": "60","residential":"30", "tertiary": "40","Trunk": "90"}.get(row["highway"], "30"),
    axis=1
)

# === Group by city and road name ===
gdf_named = gdf[gdf["name"].notnull()]
grouped = gdf_named.groupby(["city", "name"]).agg({
    "osm_id": "first",
    "highway": "first",
    "lanes": "first",
    "maxspeed": "first",
    "surface": "first",
    "bridge": "max",
    "tunnel": "max",
    "lit": "max",
    "sidewalk": "max",
    "oneway": "max",
    "cycleway": "max",
    "segment_length": "sum",
    "segment_width": "mean",
    "mean_curvature": "mean"
}).reset_index()

# === Save ===
columns = ["city", "osm_id", "name", "highway", "lanes", "maxspeed", "surface",
           "bridge", "tunnel", "lit", "sidewalk", "oneway", "cycleway",
           "segment_length", "segment_width", "mean_curvature"]

# drop roads that  segments are null
grouped = grouped[(grouped["mean_curvature"] != 0) & (~grouped["mean_curvature"].isna())]
grouped[columns].to_csv("roads_with_residential.csv", index=False)
print(" Done! Saved to roads_with_residential.csv")
