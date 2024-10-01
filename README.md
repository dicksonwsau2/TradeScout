# TradeScout

TradeScout is a tool for processing trades, calculating profit/loss summaries, and sending updates to Discord channels. The project uses SQLite as the backend database and Discord webhooks for notifications.

## Features
- Fetches trade data from an SQLite database.
- Calculates various trade metrics, including profit/loss, win rate, and PCR (Premium Captured Ratio).
- Sends formatted reports to Discord channels or threads.
- Supports capturing screenshots of a trading application and uploading them to Discord.
- Configurable through a `config.yaml` file.

## Installation

1. Clone the repository:
   `git clone <repository-url> && cd TradeScout`

2. Create a virtual environment:
   `python -m venv venv`

3. Activate the virtual environment:

   - On Windows:
     `venv\Scripts\activate`
   - On macOS/Linux:
     `source venv/bin/activate`

4. Install the dependencies:
   `pip install -r requirements.txt`

## Configuration

Modify the `config/config.yaml` file to specify the database path and Discord webhooks.

### Example `config.yaml`:

## Path to the SQLite database file
db_path: "data/data.db3"

## Webhook settings for Discord
webhooks:
  - url: "https://discord.com/api/webhooks/WEBHOOK_ID"
    thread_id: "THREAD_ID"  # Optional: If provided, sends the message to a specific thread. If not, the message goes to the main channel.
  - url: "https://discord.com/api/webhooks/ANOTHER_WEBHOOK"
    # No thread_id provided; the message will go to the main webhook channel.

## Notes:
  - db_path: This specifies the location of the SQLite database file.
  - webhooks: You can configure one or more webhooks for sending notifications. Each webhook can optionally include a thread_id to send messages to a specific Discord thread.

## Usage:
You can run the tool with the following command-line options: python trade_scout.py --date 20240920 --win restore

## Available Command-Line Options:
    --date YYYYMMDD: Specify the date for processing trades. If omitted, the current date will be used.
    --win max|restore: Adjust the window size before taking a screenshot. Use max to maximize the window, or restore to restore it if minimized.
    --noimage: Disable screenshot capturing and image upload to Discord.
    --debug: Print the message to the console and save the screenshot to a local file, without sending it to Discord.

## Features:
    Screenshot Capture: Takes a screenshot of the trading application window and uploads it to Discord.
    Report Sending: Sends a detailed report to Discord, including trade metrics such as:
      - Premium Sold
      - Premium Captured
      - PCR (Premium Captured Ratio)
      - Win Rate
      - Expired Trades and Stops
      - Weekly and Monthly Profit/Loss Summaries

## Example Output:

2024 Sep 20 (Friday)
-------------|--------------
Prem Sold    |    $14,500.00
Prem Cap     |  ($10,091.01)
PCR          |       -69.59%
Win %        |        30.00%
Exp : Stp    |           3:7
Bad Slip     |             2
-ve Exprd    |             0
Wkly PL      |   ($1,711.87)
Mth PL       |    $17,425.42

## License:
    This project is licensed under the MIT License. See the LICENSE file for details.