#!/usr/bin/env python3
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import click
import pandas as pd
import requests
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


def process_directory_element(directory_element):
    # Convert attributes to dictionary
    attributes_dict = dict(directory_element.attrs)

    # Extract values from genre, country, director, writer, and role tags
    genre_tags = directory_element.find_all("genre")
    country_tags = directory_element.find_all("country")
    role_tags = directory_element.find_all("role")

    genres = [tag["tag"] for tag in genre_tags]
    countries = [tag["tag"] for tag in country_tags]
    roles = [tag["tag"] for tag in role_tags]

    attributes_dict["genres"] = genres
    attributes_dict["countries"] = countries
    attributes_dict["roles"] = roles

    return attributes_dict


def strip_query_params_except_token(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Get the query parameters
    query_params = parse_qs(parsed_url.query)

    # Filter out the 'X-Plex-Token' parameter
    filtered_params = {key: value for key, value in query_params.items() if key.lower() == "x-plex-token"}

    # Reconstruct the URL without the filtered parameters
    new_query_string = urlencode(filtered_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query_string))

    return new_url


@click.group()
def cli():
    pass


@cli.command()
@click.argument("url")
@click.argument("xml_file_prefix")
def download(url, xml_file_prefix):
    xml_path = Path(f"{xml_file_prefix}_{date.today().isoformat()}.xml")

    stripped_url = strip_query_params_except_token(url)

    print(stripped_url)

    r = requests.get(stripped_url)
    r.raise_for_status()

    xml = r.text

    if not xml:
        raise "Unable to extract data"

    with open(xml_path, "w") as f:
        f.write(xml)
    print(f"Saved XML to {xml_path}")


@cli.command()
@click.argument("xml_path", type=click.Path(exists=True, dir_okay=False))
def csv(xml_path):
    with open(xml_path, "r") as f:
        xml = f.read()

    soup = BeautifulSoup(xml, "lxml")

    if soup.find("video") is not None:
        data = [process_video_element(elem) for elem in soup.find_all("video")]
    elif soup.find("directory") is not None:
        data = [process_directory_element(elem) for elem in soup.find_all("directory")]
    else:
        raise ValueError("Unable to find elements to process in XML")

    df = pd.json_normalize(data)

    csv_path = Path(xml_path).with_suffix(".csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV to {csv_path}")


if __name__ == "__main__":
    cli()
