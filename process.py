#!/usr/bin/env python3
import sys
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


def process_video_element(video_element):
    # Convert attributes to dictionary
    attributes_dict = dict(video_element.attrs)

    # Extract nested attributes from media and part tags
    media_element = video_element.media
    part_element = media_element.part

    media_attributes_dict = dict(media_element.attrs)
    part_attributes_dict = dict(part_element.attrs)

    attributes_dict["media"] = media_attributes_dict
    attributes_dict["media"]["part"] = part_attributes_dict

    # Extract values from genre, country, director, writer, and role tags
    genre_tags = video_element.find_all("genre")
    country_tags = video_element.find_all("country")
    director_tags = video_element.find_all("director")
    writer_tags = video_element.find_all("writer")
    role_tags = video_element.find_all("role")

    genres = [tag["tag"] for tag in genre_tags]
    countries = [tag["tag"] for tag in country_tags]
    directors = [tag["tag"] for tag in director_tags]
    writers = [tag["tag"] for tag in writer_tags]
    roles = [tag["tag"] for tag in role_tags]

    attributes_dict["genres"] = genres
    attributes_dict["countries"] = countries
    attributes_dict["directors"] = directors
    attributes_dict["writers"] = writers
    attributes_dict["roles"] = roles

    return attributes_dict


if __name__ == "__main__":
    xml_path = Path(sys.argv[1])
    with open(xml_path, "r") as f:
        xml = f.read()

    soup = BeautifulSoup(xml, "lxml")

    data = [process_video_element(elem) for elem in soup.find_all("video")]

    df = pd.json_normalize(data)

    csv_path = xml_path.with_suffix(".csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved to {csv_path}")
