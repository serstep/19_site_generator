import json, mistune, os
from os import path
from jinja2 import Environment, FileSystemLoader
import shutil


CONFIG_PATH = "config.json"
ARTICLES_SOURCE_PATH = "articles"
TEMPLATES_PATH = "templates"
DESTINATION_PATH = "built"
ASSETS_PATH = "assets"


def load_config_data():
    try:
        with open(CONFIG_PATH) as config_file:
            config_data = json.load(config_file)

        return config_data
    except (ValueError, OSError):
        return None


def load_article(filepath):
    try:
        with open(filepath) as article_file:
            return article_file.read()
    except OSError:
        return None


def load_all_articles(config_data):

    for article in config_data["articles"]:
        article["content"] = load_article(path.join(ARTICLES_SOURCE_PATH, article["source"]))


def build_index_page(config_data):
    environment = Environment(loader=FileSystemLoader("templates"))
    environment.filters["basename"] = path.basename

    index_template = environment.get_template("index.html")
    dump_path = path.join(DESTINATION_PATH, "index.html")
    index_template.stream(config_data).dump(dump_path)  


def get_article_html_filepath(article):
    new_filename = path.basename(article["source"]).replace(".md", ".html")
    return path.join(DESTINATION_PATH, article["topic"], new_filename)


def copy_assets():
    try:
        shutil.copytree(ASSETS_PATH, path.join(DESTINATION_PATH, ASSETS_PATH))
    except (shutil.Error, FileExistsError):
        print("Assets are already copied.")

def create_catalogues_for_topics(topics):
    for topic in topics:
        topic_dir_path = path.join(DESTINATION_PATH, topic["slug"])
        os.makedirs(topic_dir_path, exist_ok=True)


def build_articles_pages(config_data):
    create_catalogues_for_topics(config_data["topics"])

    environment = Environment(loader=FileSystemLoader("templates"))
    environment.filters["markdown"] = mistune.markdown

    article_template = environment.get_template("article.html")

    for article in config_data["articles"]:
        article_html_filepath = get_article_html_filepath(article)
        article_template.stream(article).dump(article_html_filepath)

if __name__ == "__main__":
    config_data = load_config_data()

    if config_data is None:
        print("Can not load  config")
        exit(1)

    load_all_articles(config_data)
    build_index_page(config_data)
    build_articles_pages(config_data)
    copy_assets()
