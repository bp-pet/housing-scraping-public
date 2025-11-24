import os
import re
import time
import logging
import datetime
import contextlib

import src.settings as settings
from src.email_utils import EmailSender

from bs4 import BeautifulSoup
from pydantic import BaseModel

with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    # to disable pygame welcome message
    import pygame


pygame.mixer.init()
known_results = dict()
email_sender = EmailSender()


class TargetSite(BaseModel):
    """Represents a site that will be scraped."""
    name: str
    codename: str
    url: str
    sound_file_name: str
    for_rent_text: str | None = None


def check_results(site: TargetSite, page_source: str) -> None:
    """Check a page for new results."""
    soup = BeautifulSoup(page_source, "html.parser")
    found_results = []

    # TODO move this logic somewhere else
    # TODO fix typing
    if site.codename == "Site 1":
        cards = soup.find_all("div", class_=re.compile("card-woning"))
        for card in cards:
            status = list(card.find("span", class_=re.compile("badge")).children)[2].text.strip() # type: ignore
            if status != site.for_rent_text:
                break
            found_results.append(card.find("a").text.strip()) # type: ignore
    elif site.codename == "Site 2":
        cards = soup.find_all("div", class_=re.compile("card-result"))
        for card in cards:
            status = card.find("span").text.strip() # type: ignore
            if status != site.for_rent_text:
                break
            found_results.append(card.find("a").text.strip()) # type: ignore
    else:
        raise Exception("Site not implemented")

    if site.name not in known_results:
        # first run just record results
        if not found_results:
            logging.warning(f"No initial results for {site.name}")
        logging.info(f"Initial results for {site.name}: {found_results}")
        known_results[site.name] = found_results
    else:
        found_new = []
        for found in found_results:
            already_exists = False
            for known in known_results[site.name]:
                if known in found or found in known:
                    # sometimes a word is added or removed from the name
                    already_exists = True
            if not already_exists:
                found_new += found

        if not found_new:
            logging.info(f"Nothing new found for {site.name}")
        else:
            notification = f"{datetime.datetime.now()} New apartment{'s' if len(found_new) > 1 else ''} in {site.name}: {found}"
            known_results[site.name] += found
            email_sender.send_email(notification)
            logging.info(notification)
            if settings.sounds_on:
                for _ in range(5):
                    # TODO add parameters to settings
                    pygame.mixer.music.load(f"sounds\\{site.sound_file_name}")
                    pygame.mixer.music.play()
                    time.sleep(5)