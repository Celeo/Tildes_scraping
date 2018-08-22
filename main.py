#!/usr/bin/env python3
"""Tildes scraping utility

Usage:
  main.py scan_all_groups [--scan_comments] [--cookie=<cookie>]
  main.py scan_group <group> [--scan_comments] [--cookie=<cookie>]
  main.py scan_topic <group> <topic> [--cookie=<cookie>]

Options:
  -h --help                 Show this screen
  --version                 Show version
  --cookie=<cookie>         Use a session cookie instead of logging in
  --scan_comments           If true, comments will also be scanned during processing of 'scan_all_groups' and 'scan_group'
"""
from docopt import docopt
import logging
from typing import Dict

from src import load_config
from src.scrapper import (
    create_driver,
    flow_login,
    set_login_cookie,
    flow_get_all_groups,
    flow_store_all_topics_for_group,
    flow_get_comments_from_topic
)
from src.db import make_tables


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s', datefmt='%I:%M:%S')


def main():
    """Main method, takes the docopt info and starts processing."""
    args = docopt(__doc__, version='Tildes scraping utility 2.0-indev')
    config = load_config()
    make_tables()

    if args['scan_all_groups'] or args['scan_group'] or args['scan_topic']:
        do_scan(config, args)
        return

    logging.error('Unknown request')


def do_scan(config: Dict, args: Dict) -> None:
    """Handling for calling features that scan (scrape) the site."""
    try:
        # create a driver and get into the site
        driver = create_driver(config)
        if args['--cookie']:
            set_login_cookie(driver, args['--cookie'])
        else:
            flow_login(driver, config)
        group_names = flow_get_all_groups(driver, config)

        do_scan_comments_too = args['--scan_comments']
        # do the scan function
        if args['scan_all_groups']:
            for group in group_names:
                flow_store_all_topics_for_group(driver, config, group, do_scan_comments_too)
            return
        group_to_scan = args['<group>']
        if group_to_scan[0] != '~':
            logging.info(f'Correcting group "{group_to_scan}" to "~{group_to_scan}"')
            group_to_scan = '~' + group_to_scan
        if args['scan_group']:
            if group_to_scan not in group_names:
                logging.warning('Group "{}" not found on the site'.format(group_to_scan))
                return
            flow_store_all_topics_for_group(driver, config, group_to_scan, do_scan_comments_too)
            return
        if args['scan_topic']:
            if group_to_scan not in group_names:
                logging.warning('Group "{}" not found on the site'.format(group_to_scan))
                return
            flow_get_comments_from_topic(driver, config, group_to_scan, args['<topic>'])
            return
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    main()
