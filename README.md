# Tildes Scraping

A project that [scrapes](https://en.wikipedia.org/wiki/Web_scraping) off of [Tildes](https://tildes.net/).

## Installation

1. Clone the repo with `git clone https://gitlab.com/Celeo/tildes_scraping`
1. Create a virtualenv and activate it with `virtualenv env && source env/bin/activate`
1. Install deps with `pip install -r requirements.txt`
1. Make the config file with `cp src/config.example.json src/config.json`
1. Populate the config with your Tildes login
1. Run the script with `python main.py -h`

### Requirements

- Python3.7+
- Virtualenv
- A Tildes account
