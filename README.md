# Bot for scraping housing websites

**This project should only be used for sites where scraping/automation is allowed! Do not use for sites that prohibit usage of scrapers!**

## Functionality
Scrapes housing websites. If something new appears that matches the conditions, notify user.

## Features
- Runs with Selenium and allows for easy setup when starting up (i.e. logging in, inputting search parameters).
- Easy way to add logic for new sites.
- Keep track of seen ads and only report new ones, specifically ones that have the correct tag.
- Pause option.
- Off hours for pausing scraping.
- Randomized waiting time between refreshes to avoid periodic calls.
- Play a sound and send an email to a given list of addresses.
- Write logs to a separate file to see what is going on.
- Send heartbeat to target emails to make sure everything is still going fine.

## Usage
1) Create new file `params.json` with same structure as `params_template.json` and input email address and password for email that will be used to send emails to the given target email addresses.
1) Create file `sites.json` with same structure as `sites_template.json` and fill it with the desired sites to scrape.
1) Implement logic in `check_results()` of `src/site_utils.py` to work with the specific sites. Two examples are provided.
1) Run `main.py`, set up the searches (put in requirements, log in if necessary).
1) Complete the prompt that is in terminal to start scraper.

## Tips
- To use a gmail account to send emails, you need to create an app password which serves as password for this tool.
