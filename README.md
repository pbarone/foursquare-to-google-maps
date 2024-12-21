# Foursquare to Google Maps Lists Migration

This project consists of Python scripts to automate the process of exporting saved lists from Foursquare and importing them into Google Maps. It uses Foursquare's API to extract lists and Selenium to interact with Google Maps.

---

## Features

- **Export Foursquare Lists**: Extract all saved lists and their associated locations from Foursquare.
- **Upload to Google Maps**: Automatically create Google Maps lists and add places from Foursquare.
- **Error Handling**: Includes basic retry mechanisms and logs to track progress.
- **CSV Export**: Export the place data for further analysis.

---

## Prerequisites

1. **Python**: Ensure Python 3.7 or higher is installed.
2. **Google Chrome**: Latest version of Google Chrome is required.
3. **ChromeDriver**: Install the appropriate version of ChromeDriver matching your Google Chrome version.
4. **Foursquare Access Token**: Obtain an access token from Foursquare Studio ([Instructions](https://studio.foursquare.com/map/tokens.html)).

---

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/foursquare-to-google-maps.git
   cd foursquare-to-google-maps
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add the following variables:

   ```env
   FSQACCESS_TOKEN=your_foursquare_access_token
   USER_DIR=path_to_chrome_user_data_directory
   ```

   - `FSQACCESS_TOKEN`: Replace `your_foursquare_access_token` with your actual token.
   - `USER_DIR`: Replace `path_to_chrome_user_data_directory` with the path to your Chrome user data directory for managing Google account sessions.

---

## Usage

### Step 1: Export Foursquare Lists

Run the `getFSQList.py` script to export Foursquare lists and save them to a CSV file:

```bash
python getFSQList.py
```

This will generate a file named `allplaces.csv` containing the exported data.

### Step 2: Upload to Google Maps

Run the `FSQ-to-GMaps.py` script to create and populate Google Maps lists:

```bash
python FSQ-to-GMaps.py
```

This script will:

- Log into your Google account using the Chrome browser.
- Navigate to Google Maps lists and create new ones if needed.
- Add places to the lists from the CSV file.

### Important Notes

- Use this script at your own risk. It will not delete any data from existing Google Maps lists but it may add a lot of entries there and sometimes it can add the wrong place.
- Sometimes Selenium throws an error when trying to click on a place in the search results dropdown. When that happens, the script will pause and give the user the opportunity to click on the correct entry (in the Chrome window). To continue, press any key in the terminal window where the script is running.
- I consider this an alpha version; any comments and contributions would be really welcome.

---

## File Structure

- **getFSQList.py**: Extracts saved lists from Foursquare and saves them as a CSV file.
- **FSQ-to-GMaps.py**: Reads the CSV file and automates the creation and population of Google Maps lists.
- **processCSV.py:** handles reading and writing CSV files.
- **requirements.txt**: Lists all required Python dependencies.
- **.env**: Configuration file for sensitive information (not included in the repository).

---

## Dependencies

- **Selenium**: Automates interaction with Google Maps.
- **Requests**: Handles API requests to Foursquare.
- **Colorama**: Adds colored console output for better visibility.
- **RapidFuzz**: Provides string matching and similarity scoring.
- **python-dotenv**: Loads environment variables from a `.env` file.

---

## Notes

- Ensure that you are logged into your Google account in the specified Chrome user profile (`USER_DIR`) before running the scripts.
- Use the Foursquare token responsibly, as misuse may lead to rate limiting or account suspension.
- Some places may not be found in Google Maps due to differences in naming or address formats.

---

## License

This project is licensed under the CC0 License. See the ofile for more details.

---

## Acknowledgments

- [Foursquare API](https://developer.foursquare.com/) for providing access to saved lists.
- [Selenium](https://www.selenium.dev/) for browser automation.

