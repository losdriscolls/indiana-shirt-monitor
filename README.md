# United States of Dead Shirt Monitor

This repository contains a simple monitor for the Grateful Dead's **United States of Dead** collection.  It is designed to
notify you when a specific state's shirt becomes available in a particular size.

## How it works

The monitor script (`monitor.py`) performs the following steps:

1. Fetch the collection page from **Dead.net**.
2. Locate the product page for the state specified in the `STATE_KEYWORD` environment variable.
3. Retrieve the product's JSON representation from the Shopify API (using the `.json` endpoint).
4. Check if the size specified in the `SIZE_KEYWORD` environment variable is available.
5. Send a notification via [ntfy.sh](https://ntfy.sh) to the topic defined by the `NTFY_TOPIC` environment variable.

### Environment variables

The script is driven by three environment variables:

| Variable       | Description                                                     | Default     |
| -------------- | --------------------------------------------------------------- | ----------- |
| `STATE_KEYWORD`| State to watch for (e.g., `indiana`)                            | `indiana`   |
| `SIZE_KEYWORD` | Size to watch for (e.g., `large`)                               | `large`     |
| `NTFY_TOPIC`   | ntfy topic for notifications.  If unset, notifications go to STDOUT | *unset* |

## Running locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Export the required environment variables and run the script:

```bash
export STATE_KEYWORD=indiana
export SIZE_KEYWORD=large
export NTFY_TOPIC=my-ntfy-topic
python monitor.py
```

3. You will receive notifications via ntfy when the shirt is available or sold out.

## GitHub Actions workflow

This repository includes a GitHub Actions workflow (`.github/workflows/check.yml`) that runs the monitor on a schedule.  The
workflow checks every 5 minutes (customizable) and sends notifications when the product page or size changes state.

### Setup instructions

1. **Fork or clone** this repository and create a new GitHub repository.
2. In your repository's **Settings** → **Secrets and variables** → **Actions**, add a new secret named **`NTFY_TOPIC`** with the value of your ntfy topic (e.g. `andrew-indiana-tee`).
3. (Optional) In the same section, add repository variables `STATE_KEYWORD` and `SIZE_KEYWORD` if you want to track a different state or size.
4. Commit and push your changes.  The scheduled workflow will begin running and will notify you via ntfy when the shirt is available.

## Notes

This project is not affiliated with Dead.net or Shopify.  It relies on the current site structure and may require adjustments
if the site changes.  Feel free to open an issue or PR if you encounter any problems.