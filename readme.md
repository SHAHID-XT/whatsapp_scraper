
# WhatsApp Web Scraper

A Python-based web scraper for WhatsApp Web that extracts messages from contacts over the past few days. It uses Selenium, BeautifulSoup, and other libraries to automate the process of scraping WhatsApp Web chats and storing the messages in CSV format.

## Features

- Scrapes messages from WhatsApp Web.
- Supports message extraction for contacts in the past 20 days (configurable).
- Automatically scrolls through the chat to load older messages.
- Stores messages in CSV files.
- Detects and avoids duplicate messages.
- Saves contacts' chat history in individual CSV files.

## Requirements

- Python 3.x
- Selenium
- BeautifulSoup
- dotenv (for loading environment variables)
- WebDriver (Chrome or any other browser of your choice)
- Google Chrome or Chromium installed on your machine

### Install Dependencies

Install the required libraries using `pip`:

```bash
pip install selenium seleniumbase beautifulsoup4 python-dotenv
```

### Environment Setup

Create a `.env` file in the root of the project and add the following variable:

```env
DAYS=20  # Number of days of messages to extract
```

## Usage

1. **Start the Scraper:**

Run the script to start scraping WhatsApp Web:

```bash
python main.py
```

2. **How It Works:**

- The scraper opens WhatsApp Web and waits for the page to load.
- It collects messages from visible contacts by scrolling through the chat window.
- Messages are stored in CSV files, with each contact's messages stored in separate files.
- The script continues until it has gathered all available messages or reaches a limit.

## Output

- CSV files are saved in the `Contacts/` folder and all well as in the messages.json
- The messages are saved in CSV format with columns: `user`, `message`, `time`, `date`, `datetime`.

## Notes

- Make sure that you have WhatsApp Web open and logged in on your machine.
- The script will extract messages from contacts for the last 20 days (or another value you specify in the `.env` file).
- If the script is not working, try closing all other Chrome windows or instances and restarting the script.

## Customization

- You can change the number of days to scrape by modifying the `DAYS` variable in the `.env` file.
- The script saves messages in individual CSV files for each contact, named by their contact or group name. Invalid characters in the name are replaced with underscores to ensure valid file names.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
