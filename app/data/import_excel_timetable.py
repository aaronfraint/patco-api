import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
DATABASE_URL = os.getenv("DATABASE_URL", None)

XLSX_FILE = "app/data/PATCO_Timetable_2023-03-25.xlsx"

STATIONS_WB = [
    x.lower()
    for x in [
        "Lindenwold",
        "Ashland",
        "Woodcrest",
        "Haddonfield",
        "Westmont",
        "Collingswood",
        "Ferry Ave",
        "Broadway",
        "City Hall",
        "8th_and_Market",
        "9_10th_and_Locust",
        "12_13th_and_Locust",
        "15_16th_and_Locust",
    ]
]

STATIONS_EB = STATIONS_WB.copy()
STATIONS_EB.reverse()

STATION_NAMES = {
    "wb": [f"station_{x}" for x in STATIONS_WB],
    "eb": [f"station_{x}" for x in STATIONS_EB],
}

TABS = {
    "weekday_wb": "Table 1",
    "weekday_eb": "Table 2",
    "saturday_wb": "Table 6",
    "saturday_eb": "Table 7",
    "sunday_eb": "Table 9",
    "sunday_wb": "Table 10",
}


def handle_value(val: str) -> str:
    """
    Turn a value like
        '12:05 P' into '12:05'
        and
        '12:12 A' into '0:12'
        etc.
    """

    # a weird arrow symbol is used to indicate that a train
    # does not stop at this station on this trip
    if "\uf0e0" in val:
        return "Does not stop"

    try:
        val_without_ampm = val.split(" ")[0]
        hour, minute = val_without_ampm.split(":")

    except:
        print(val)
    if "A" in val:
        if "12:" in val:
            hour = 0

    elif "P" in val:
        if "12:" not in val:
            hour = int(hour) + 12

    return f"{hour}:{minute}"


def parse_tab(
    profile: str = "weekday_eb",
) -> pd.DataFrame:
    day_type, direction = profile.split("_")

    # Weekend tables have one fewer header rows to skip
    if day_type == "weekday" or profile == "sunday_eb":
        rows_to_skip = 2
    else:
        rows_to_skip = 1

    # Get the name of the tab in the excel file
    tab_name = TABS[profile]

    # Read the excel file into a dataframe
    df = pd.read_excel(
        XLSX_FILE,
        sheet_name=tab_name,
        skiprows=rows_to_skip,
    )

    # Rename the columns with the proper station order
    df.columns = STATION_NAMES[direction]

    # Iterate over all rows in the dataframe, and save a list of dictionaries
    data_list = []
    for _, row in df.iterrows():
        line_1 = {}
        line_2 = {}

        for col in df.columns:
            values = row[col]

            # Split the cell's value on the \n character
            data = values.split("\n")

            # Most tables have two times per cell...
            if len(data) > 1:
                line_1[col] = handle_value(data[0])
                line_2[col] = handle_value(data[1])
            # ... but some tables only have one value in the cell
            else:
                line_1[col] = handle_value(data[0])

        # We always save the first line, and save the second line if it exists
        data_list.append(line_1)
        if line_2 != {}:
            data_list.append(line_2)

    return pd.DataFrame(data_list)


def publish_to_postgres():
    """
    Parse each tab with timetable data,
    and write it to the Postgres database
    """
    for profile in TABS:
        print("Importing:", profile)
        df = parse_tab(profile)

        df.to_sql(
            f"timetable_{profile}",
            con=create_engine(DATABASE_URL),
            if_exists="replace",
            index=False,
        )


if __name__ == "__main__":
    publish_to_postgres()
