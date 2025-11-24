"""Entry point of program."""

import sys
import json
import time
import random
import logging
from tqdm import tqdm # type: ignore

import src.settings as settings
from src.email_utils import EmailSender
from src.other_utils import is_off_hours
from src.site_utils import TargetSite, check_results

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# TODO logs to different file every day
# TODO send one heartbeat per day with number of errors
# TODO add current list to log

logging.basicConfig(
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler(sys.stdout)
    ],
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

email_sender = EmailSender()


def setup_browser() -> None:
    """Open each site in a separate tab."""
    driver.maximize_window()
    if len(sites) == 0:
        error_message = "No sites given in config, stopping"
        logging.error(error_message)
        raise Exception(error_message)
    driver.get(sites[0].url)

    for i in range(1, len(sites)):
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[i])
        driver.get(sites[i].url)

def perform_sleep():
    """Calculate sleep time based on settings and do it."""
    sleep_time = max([
        settings.min_sleep_time_sec,
        int(random.gauss(settings.mean_sleep_time_sec,
        settings.stdev_sleep_time_sec))
    ])
    logging.info(f"Starting to sleep for {sleep_time}s")
    for i in tqdm(range(sleep_time), desc=f"Sleeping for {sleep_time:>4}s before continuing"):
        time.sleep(1)


def run():
    """Main loop of program. Sleeps, refreshes, and checks pages."""
    # TODO this should be an event-based system instead of sleeps; or at least async
    # that would also allow different timing for each site, which can be useful
    checks_completed = 0
    while True:

        if checks_completed > 1000:
            email_sender.send_email("Heartbeat: 1000 successful refreshes")
            checks_completed = 0
            # TODO this part needs to be made much better
            # TODO add number of errors to heartbeat

        if settings.enable_off_hours and is_off_hours():
            # TODO change to just wait the appropriate time until off hours are over
            logging.info("Off hours")
            perform_sleep()
            continue
        
        if len(driver.window_handles) != len(sites):
            # use this as pausing option: open empty tab to pause execution
            # closing the extra tab will automatically resume
            logging.info("Paused by user")
            perform_sleep()
            continue

        for site_index, site in enumerate(sites):
            driver.switch_to.window(driver.window_handles[site_index])
            try:
                driver.refresh()
            except Exception as e:
                logging.warning(f"Error while refreshing {site.name}: {e}")
                continue
            time.sleep(2)
            check_results(site, driver.page_source)
            checks_completed += 1
            time.sleep(5)
        logging.info("Page refreshes completed")
        perform_sleep()
        




if __name__ == "__main__":

    logging.info("Starting")

    # load site settings
    with open("config/sites.json", 'r') as f:
        site_dict = json.loads(f.read())
    sites = [TargetSite(**d) for d in site_dict]

    driver = webdriver.Firefox()

    setup_browser()

    while True:
        if input("Type 'START' and enter once searches are set up: ") == "START":
            break

    try:
        run()
    except Exception as e:
        email_sender.send_email(f"Program stopped due to exception: {e}")