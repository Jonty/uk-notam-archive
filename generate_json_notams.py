import json
import os
from datetime import datetime
import time

from lxml import etree
from geojson import Point, Feature, MultiPolygon
from turfpy.transformation import circle

from notam_lookup_data import (
    NOTAM_TYPES,
    NOTAM_SCOPES,
    NOTAM_SERIES,
    NOTAM_SUBJECTS,
    NOTAM_CONDITIONS,
    NOTAM_TRAFFIC,
    NOTAM_PURPOSES,
)

# Todo:
# "Active" / "Inactive" status on notams, maybe as a directory? Dict key?
# Go back and add an "unpublished date" when notams are no longer listed in the PIB
# * Walk every commit in repo outputting the json files for it, and amending the commits (or adding another commit?). Add this script to the repo so it can be used to re-process/re-write all notam data later if needed.
# * If this is not type R and the file already exists, and the file contents we are about to write is different than the existing file, throw an exception
# * Handle Type==R, ReferredSeries/ReferredNumber/ReferredYear - should update the previous notam's json with a reference to this one
# * Correct NOTAM subjects
# * HTML pages and index for every notam
# * parse free text for:
#   * complex geometries
#   * contact details
#   * references to briefing sheets and other notams
#   * hours of operation
#   * references to coordinates
# * Index on contact details
# * Client-side search
# * Sqlite DB
# * RSS feeds for regions defined by polygons in a json file and named (for slack)
# * laser and firework and drone swarm announcement bots
# * "current" data directory, that just contains the currently active notams, and a metadata file for when it was generated. Or maybe just a file that lists all the ID's?
# * Move "data" to "scraped"


def convert_coords(coord_str):
    # Split into latitude and longitude parts
    lat = coord_str[0:4]  # First 4 chars for latitude
    lat_dir = coord_str[4]  # N/S
    lon = coord_str[5:10]  # Next 5 chars for longitude
    lon_dir = coord_str[10]  # E/W

    # Convert latitude: first 2 digits are degrees, last 2 are minutes
    lat_deg = float(lat[:2])
    lat_min = float(lat[2:])
    lat_decimal = lat_deg + (lat_min / 60)
    if lat_dir == "S":
        lat_decimal = -lat_decimal

    # Convert longitude: first 3 digits are degrees, last 2 are minutes
    lon_deg = float(lon[:3])
    lon_min = float(lon[2:])
    lon_decimal = lon_deg + (lon_min / 60)
    if lon_dir == "W":
        lon_decimal = -lon_decimal

    return (lat_decimal, lon_decimal)


def pib_to_json(pib_xml, existing_notams={}):
    tree = etree.fromstring(pib_xml)

    # Parse the areodromes
    notams = tree.findall(".//Notam")
    for notam in notams:
        series = notam.find("./Series").text
        number = notam.find("./Number").text
        year = int(notam.find("./Year").text)
        notam_id = f"{series}{number}/{year}"

        if notam_id in existing_notams:
            continue

        notam_type = notam.find("./Type").text
        if notam_type not in NOTAM_TYPES:
            raise Exception(f"Unhandled NOTAM type '{notam_type}' in {notam_id}")

        replaces = None
        if notam_type == "R":
            r_series = notam.find("./ReferredSeries").text
            r_number = notam.find("./ReferredNumber").text
            r_year = int(notam.find("./ReferredYear").text)
            replaces = {
                "id": f"{r_series}{r_number}/{r_year}",
                "series": r_series,
                "number": int(r_number),
                "year": r_year,
            }

        store_date = notam.find("./NotamStoreDate").text
        store_date_parsed = datetime.strptime(store_date, "%d%m%Y%H%M")

        start_date = notam.find("./StartValidity").text
        end_date = notam.find("./EndValidity").text
        if end_date == "PERM":
            end_date_parsed = None
        else:
            end_date_parsed = datetime.strptime(end_date, "%y%m%d%H%M").isoformat()

        coordinates = notam.find("./Coordinates").text
        latlon = convert_coords(coordinates)

        radius_text = notam.find("./Radius").text
        radius = radius_km = None
        if radius_text != "999":
            radius = float(radius_text)
            radius_km = radius * 1.852

        qline_node = notam.find("./QLine")

        lower = int(qline_node.find("./Lower").text)
        upper = int(qline_node.find("./Upper").text)
        if lower == 0 and upper == 999:
            lower = upper = None
        else:
            # Q line FL is expressed in hundreds of feet
            lower *= 100
            upper *= 100

        subject = qline_node.find("./Code23").text
        condition = qline_node.find("./Code45").text
        traffic = qline_node.find("./Traffic").text
        purpose = qline_node.find("./Purpose").text

        data = {
            "id": notam_id,
            "id_fields": {
                "series": series,
                "number": int(number),
                "year": year,
            },
            "type": NOTAM_TYPES[notam_type],
            "replaces": replaces,
            "replaced_by": None,
            "date": {
                "published": store_date_parsed.isoformat(),
                "unpublished": None,
                "valid_from": datetime.strptime(start_date, "%y%m%d%H%M").isoformat(),
                "expires_at": end_date_parsed,
            },
            "qualifiers": {
                "scopes": [NOTAM_SCOPES[s] for s in qline_node.find("./Scope").text],
                "traffic_code": traffic,
                "traffic_types": [NOTAM_TRAFFIC[t] for t in traffic],
                "purpose_code": purpose,
                "purpose_types": [NOTAM_PURPOSES[p] for p in purpose],
            },
            "icao": {
                "NOF": notam.find("./NOF").text,
                "FIR": qline_node.find("./FIR").text,
                "aerodrome": notam.find("./ItemA").text,
            },
            "info": {
                "series_code": series,
                "series_description": NOTAM_SERIES[series],
                "subject_category": NOTAM_SUBJECTS[subject]["category"],
                "subject_code": subject,
                "subject_description": NOTAM_SUBJECTS[subject]["description"],
                "condition_code": condition,
                "condition_description": NOTAM_CONDITIONS[condition],
                "text": notam.find("./ItemE").text,
            },
            "other": {},
            "area": {
                "dms_coordinates": coordinates,
                "radius_nm": radius,
                "center_latitude": latlon[0],
                "center_longitude": latlon[1],
                "radius_km": radius_km,
                "lower_altitude_ft": lower,
                "upper_altitude_ft": upper,
                "complex_geometry": False,
                "geojson": None,
            },
        }

        # FIXME: Need mapping to actual names
        # B: Effective from (begins)
        # C: Effective until (ends)
        # D: Planned schedule (e.g. 1500-1600, 0430-0500)
        #    Loads of formats for this, and: Sunrise-Sunset (SR-SS) may follow the day(s) or “DLY”.
        # F: Lower limit (FL090, 3000FT AMSL) / SFC == surface / FL250 == 25000ft
        # G: Upper limit, same again - "when expressed as a flight level (FL) or altitude (AMSL) the associated FL values will also be applied in the Q line
        for letter in ("B", "C", "D"):  # , "F", "G"):
            node = notam.find("./Item" + letter)
            if node is not None:
                data["other"]["item_" + letter.lower()] = node.text

        geometries = []
        if data["area"]["radius_km"]:
            center = Feature(
                geometry=Point(
                    (data["area"]["center_longitude"], data["area"]["center_latitude"])
                )
            )
            # FIXME: Calculate steps more intelligently
            cc = circle(
                center,
                radius=data["area"]["radius_km"],
                units="km",
                steps=int(radius * 10),
            )
            geometries.append(cc.geometry.coordinates)

        data["area"]["geojson"] = MultiPolygon(geometries)

        yield data


def write_json(notam):
    dirs = f'json/20{notam["id_fields"]["year"]}'
    os.makedirs(dirs, exist_ok=True)

    filename = f'{notam["date"]["published"]}_{notam["id"].replace("/", "_")}.json'
    path = f"{dirs}/{filename}"
    with open(path, "w") as f:
        json.dump(notam, f, indent=4, separators=(",", ": "))

    return path


if __name__ == "__main__":
    with open("data/PIB.xml", "rb") as file:
        pib_body = file.read()

    for json_notam in pib_to_json(pib_body):
        write_json(json_notam)
