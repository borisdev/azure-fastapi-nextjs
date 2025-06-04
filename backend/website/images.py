"""
Script make images for each subreddit display name

Example Input

    - Anxiety.FetchedSubreddits.json

Example Output

    - static/images/anxiety.png
"""

import json
from pathlib import Path

import requests
from common import settings
from common.settings import DATA_DIR
from loguru import logger
from openai import OpenAI
from PIL import Image

# source_file_path = (
#     Path(DATA_DIR)
#     / "subreddits"
#     / f"subreddit_{subreddit_name}_submissions.json"
# )
#
# with open(source_file_path, "r") as f:
#     data = json.load(f)


client = OpenAI(api_key=settings.openai_api_key)

# Figure these out later


errors = [
    "EatingDisorders",
    "COVID19",
    "Borderline",
    "BingeEatingDisorder",
    "EDAnonymous",
    "eating_disorders",
    "bipolar2",
    "BPD",
    "BipolarReddit",
    "bulimia",
    "fuckeatingdisorders",
    "covid19stack",
    "schizophrenia",
    "edsupport",
    "BipolarDisorderReddit",
    "bipolar",
    "Coronavirus",
]


def get_subreddit_names():
    source_dir = Path(DATA_DIR) / "subreddits"
    key_files = [f for f in source_dir.glob(f"*.json")]
    print(key_files)
    print("File count:", len(key_files))
    return key_files


def load_subreddit_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


# response = client.images.generate(
#     model="dall-e-3",
#     prompt=f"""pencil drawing of Achilles Tendinopathy
#         """,
#     size="1024x1024",
#     quality="standard",
#     n=1,
# )
#
# image_url = response.data[0].url
# print(image_url)
#
# response = client.images.generate(
#     model="dall-e-3",
#     prompt=f"""Pencil drawing of Transcranial Direct Current Stimulation (tDCS) for ADHD symptoms in adolescent boys.
#         """,
#     size="1024x1024",
#     quality="standard",
#     n=1,
# )
#
# image_url = response.data[0].url
# print(image_url)
#


def get_image_url(topic: str):
    prompt = f"""
        Topic: Do it your self (hacking) you performance on treating {topic}
        Art mode: Pencil drawing
        Style: Minimalist, Fun, Clean, Thoughful, Inspirational

        """
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    return image_url


# >LIGHT PATSEL TOURQUOISE BLUE PALE
def generate_images():
    inputs = get_image_gen_inputs()
    count = len(inputs)
    errors = []

    for idx, input in enumerate(inputs):
        print("prompt:", input["prompt"])
        try:
            image_url = get_disorder_image(prompt=input["prompt"])
            # print(image_url)
            # download image
            # requests.download_image(image_url, f"{input['display_name']}.png")
            response = requests.get(image_url)
            file_path = Path("static/images") / f"{input['display_name']}.png"
            with open(file_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Image {idx+1}/{count} downloaded for {input['display_name']}")
            logger.success(f"Saved image to {file_path}")
        except Exception as e:
            logger.error(f"Failed to download image for {input['display_name']}")
            logger.error(e)
            errors.append(input["display_name"])
    # TEST
    print("Errors:", errors)


if __name__ == "__main__":
    # subreddit_name = "ADHD"
    # topic = "ADHD (Attention Deficit Hyperactivity Disorder)"
    subreddit_name = "sleep"
    topic = "Sleep Biohacking"
    sink_path = Path("static/images_png")
    sink_file_path = sink_path / f"{subreddit_name}.png"
    image_url = get_image_url(topic)
    response = requests.get(image_url)
    with open(sink_file_path, "wb") as f:
        f.write(response.content)
    print(f"Saved image to {sink_file_path}")

    """
    Convert topic images from png to jpg
    """
    source_dir = Path("static/images_png")
    source_file_path = source_dir / f"{subreddit_name}.png"
    sink_dir = Path("static/images")
    # files = [f for f in source_dir.glob("*.png")]
    png_image = Image.open(source_file_path)
    file_path = sink_dir / f"{subreddit_name}.jpg"
    png_image.convert("RGB").save(file_path)
    logger.success(f"Converted {source_file_path} to {file_path}")
