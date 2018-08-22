#!/usr/bin/env python3
"""Tildes scrapping utility

Usage:
    main.py scan_all [--scan_comments]
    main.py scan_topic <group> [--scan_comments]
    main.py scan_comments <group> <topic>

Options:
    -h --help               Show this screen
    --version               Show version
    --no-next               Don't click the next buttons in groups
    --topic-count=<count>   Set the number of topics to show in a group [1 -> 100, default: 100]
"""
from docopt import docopt
import logging

from src import load_config
from src.scrapper import create_driver, flow_login, flow_get_all_groups, flow_store_all_topics_for_group, driver_pause
from src.db import make_tables


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s', datefmt='%I:%M:%S')


def main():
    args = docopt(__doc__, version='Tildes scrapping utility 1.0')
    config = load_config()
    driver = None
    make_tables()

    try:
        if args['scan_all'] or args['scan_topic'] or args['scan_comments']:
            driver = create_driver(config)
            flow_login(driver, config)
            group_names = flow_get_all_groups(driver, config)
            if args['scan_all']:
                for group in group_names:
                    flow_store_all_topics_for_group(driver, config, group)
                    driver_pause(3)
                return
            if args['scan_topic']:
                if args['<group>'] not in group_names:
                    logging.warning('Group "{}" not found on the site'.format(args['<group>']))
                    return
                flow_store_all_topics_for_group(driver, config, args['<group>'])
                return
            if args['scan_comments']:
                if args['<group>'] not in group_names:
                    logging.warning('Group "{}" not found on the site'.format(args['<group>']))
                    return
                logging.error('Feature not yet implemented')
                return
    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    main()
