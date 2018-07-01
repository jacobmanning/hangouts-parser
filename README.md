# hangouts-parser

This repository parses conversation data from Google Hangouts and gives
diagnostics on the number of messages in conversations. Two scripts are
currently supported: `parser.py` and `visualize.py`. The parsing script parses
raw JSON data from Google Takeout and creates pickled summary files for each
conversation. The visualization script creates a histogram of messages over
time using the pickled conversation summaries.

## Usage
1. Clone this repository
2. Download your hangouts data
    + Navigate to [Google Takeout](https://takeout.google.com/settings/takeout)
    + Choose "Select None" and manually select Hangouts
    + Download the data in zip format and move the `Hangouts.json` file into the `raw` folder in this repository
3. Install dependencies via `pip`
    + `pip install -r requirements.txt`
    + No dependencies are required for the `parser.py` script, but `visualize.py` requires the dependencies
4. Run the parser
    + **Note:** if you did not place your hangouts data as `raw/Hangouts.json` you can specify the path to the `.json` file as an argument to the `parser.py` script via the `-f` flag
```bash
python parser.py
```
5. Run the visualization
    + The `<conversation_id>` can be found in the output of the `parser.py`
      script
```bash
python visualize.py -f output/<conversation_id>.pkl
```

### License
This code is freely available under the GNU Public License (GPL).

### Privacy notice
> All of the data processing in these scripts happens locally on your computer. The data you provide to the script is **NOT** uploaded to an external server. Feel free to examine the code if you are concerned.

### Acknowledgements
> This repository was inspired by [MasterScrat/Chatistics](https://github.com/MasterScrat/Chatistics). Chatistics can parse Facebook Messenger and Telegram data, but not Hangouts group messages. I originally intended to contribute to that repository and add Hangouts group message support, but my design drifted far from the existing design in that repository so I created a new project. Shoutout to MasterScrat for great work and thanks for the inspiration!
