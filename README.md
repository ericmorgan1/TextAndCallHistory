# TextAndCallHistory
Visualize text message and call history.

## Dependencies
1. This uses the outputs from [iExplorer](https://macroplant.com/)
2. You must have [Python](https://www.python.org/) installed

## Instructions

### 1. Copy Data
* Export your call history and/or text message history from iExplorer
* Copy the files into the folder with the code

### 2. Configuration
* Open `go.py` 
* Update `CALL_HSITORY_FILE_NAME` to have the file with your call history
* Update `TEXT_HISTORY_FILE_NAME` to have the file with your text message history
* Update `PHONE_NUMBER` to have the phone number that you want to filter on (for call history)

### 3. Run the code
* Run `go.py`

### 4. View the results
* Call history summary appears in the console screen
* Open `timeline/timeline.html` in a browser to view the text/call timeline
