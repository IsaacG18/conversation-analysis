# Conversation analyst

To get this code running require steps for set up

# Step 1 install python and pip
You need to have Python 3.11 installed on your system. If you haven't installed it yet, you can download it from the [official Python website](https://www.python.org/downloads/) and follow the installation instructions for your operating system.

To verify if pip is installed, you can run the following command in your terminal or command prompt:

    pip --version

# Step 2 clone the repo

    git clone https://github.com/IsaacG18/conversation-analysis.git

To switch version, checkout a version branch, recommend to uses 2.1.0

    git checkout -t <remote-branch-version>

# Step 3 set up venv

    pip install virtualenv

Navigate to your project directory in the terminal or command prompt and run the following command to create a virtual environment named 'ca':

    virtualenv ca

**On Windows:**

    ca\Scripts\activate

**On macOS and Linux:**

    source ca/bin/activate

# Step 4 add .env

File path: conversation-analysis/tp3/tp3 **create a file** called **.env**

Add in the file

    CHATGPT_API_KEY=<api-key>
    CHATGPT_VERSION=<model-version>
    NLP_VERSION=<nlp-version>

Current chatgpt  version is gpt-3.5-turbo

Current NLP version is en_core_web_md, this is also the default NLP if nothing is selected

If the key needs updated the .env and re-run Step 7

# Step 5 install packages
File path: conversation-analysis/

Using Init Script you can skip Step 5 and 6 using

    chmod +x init.sh

    ./init.sh

Or for windows

    init.bat

**For manual install:**d
**Window OS:**

    pip install -r win_requirements.txt

**Other OS:**

    pip install -r requirements.txt

# Step 6 run these commands
Create and run the migrations 
File path: conversation-analysis/tp3:

    python manage.py makemigrations
    
    python manage.py migrate
    
    python manage.py migrate --run-syncdb

Run the populate script

    python date_format_populate.py

# Step 7 After set up to run the website uses this command
File path: conversation-analysis/tp3

    python manage.py runserver

# To test the speed of the code run this in linux
File path: conversation-analysis/tp3
    
    time python speed_test_messages.py

To run the file 30 times do this

    time (for i in {1..30}; do python speed_test_messages.py; done)

# Change NLP
To change the NLP data set

    python -m spacy download <data-set-name>

it must be imported then update .env

# Versions

  

**1.0.0**
Available from the 15th of January
Access original only on Python Anywhere

Core Feature:
- NLP
  - Sentiment Analysis (not integrated)
  - Added Visualization for messages
  - Keyword Identification
  - Name and Location identification
- Data ingestion
  - Basic Customization of File ingestion
  - Custom Keywords (only in settings)
  - Compatibility with csv, docs, and txt
  - Error Handling in upload
- Front End
  - Search homepage for files
  - Word highlighting in content review
  - Date Filtering 
  - Key Highlighting
- ChatGPT
  - Nothing Implemented
  
**2.0.0**
Available from the 15th of February, available as github and website
- Content Review New features
  - Google Maps API search
  - Export XML data
  - Add re-analysis of file
- ChatGPT new features
  - Added the ability to message chatgpt
  - Added ability to create new chats
  - Added ability to access old chats
  - Added suggested prompts based on analysis
- Other new features
  - Renaming analysis on homepage
- Improvements to existing features
  - Search for root words in analysis
  - Improved customization in file structure including; dates, types order, and ability to added extra delimiters

**2.1.0**
Available from the 15th of March, available as github and website
- Visual updates
  - Content Review Page
  - ChatGPT page
  - Waiting message for data analysis 
  - Show all risk words
  - Messages indicating what dates are being filtered
- New features
  - ChatGPT summary
  - Search bar on chatgpt page
  - Allow the renaming of chats
  - Customisation of risk levels
  - Increased navigation between chatgpt page and content review
  - Allow chatgpt to find names and locations
  - Ability to delete old analysis
  - Ability to select to skip a line as title line
  - initialization script
  - Ability to deal with a title row in data ingestion
  - Ability to read past missing lines
  - Remove UNIX timestamp
  - Remove non analysed files from homepage
  - Reset filters button
- Other improvements
  - Cleaner code
  - Increase testing
  - Bug fixes on display html in chats
  - Filter out emojis from names
  - Less files stored on machine
  - Update readme
  - More interchangeable LLM and NLP
  - Add a walk through
  - Save sentiment and strictness properly




# Application Overview
This project is primarly for local running usage
**HomePage**:
This is the main page which displays all of your uploaded files.

 - There is a search bar at the top right hand side that can be  used to filter through your uploaded files by name.
 - Next to the search bar there is three buttons: Upload File, Setttings, and ChatGBT.
 - Clicking on an uploaded file will lead you to the analysis page. These files can also be deleted if the "x" icon is pressed.
 - Double clicking on an uploaded file will allow you to rename it.
 - Clicking to "Conversation Analyst" on the top left-hand side will always lead the user back to the home page.

**Analysis Page**:
The app uses Natural Language Processing (NLP) to analyse text documents and generate reports.

- The system then processes the document and displays key information.
- Filtering on this page only works one at the time.
- There is a reset filter
- What is analysed:
  - Names
  - Locations
  - Custom Inputted Keyword (Lemmas of each word)
  - Risk Level (Based of keywords and risk values multiplied by the sentiment)

**Upload Page**:
On the upload page users can see a "Browse" button which allows them to upload a file.

- The application currently supports .txt, .csv, and .docx.
- Custom delimiters can be set with default delimiter set to "," for "Timestamp" and ":" for Sender. (Order can be altered but message has to appear in the end)
- Timestamp Formats must also be selected.
- Supported Timestamp Formats:
  - ISO 8601
  - Common Log Format
  - ISO 8601 Without Seconds

- Suites and keywords risk factor are used to filter results based upon their level. The higher the number the riskier the keyword.
- After successfully uploading a file user will be redirected to the analysis page.

**Settings Page**:
Keywords and Detection settings can be customized here.

- In keyword tab, suites and keywords can be added and removed
- In detection tab, the level of strictness and sentiment and be adjusted from high to low
  - This adjustment can range from high to low, offering a balance between precision and recall based on the user's preference or requirements for the analysis.
  - Users can tweak how sentiment analysis is conducted. This may involve adjusting the sensitivity of the sentiment analysis tool, enabling the application to more accurately reflect the tone and mood of the conversations being analysed.

**ChatGBT Page**:
This page allows you to interact with the AI model directly. Suggested prompts are also offered.

- You can type in any message and get suggestions for what to say next.
- When messages are parsed they are only filtered by time.
- Search bar to filter through chat history.
- Multiple conversation can be made simultaneously.
- Conversations can be renamed by double clicking them.

# Get Started

- **What can you do with the website**
  - upload chat logs
  - receive analysis of the chat logs
  - tailor analysis with customise settings
  - download analysis as XML files
  - get boosted from external APIs
- **Upload files**
![screenshot of upload page](image.png)
  - upload file with the 'upload' button at the right end of the navigation bar
  - adjust delimiter settings according to the format of your files
  - reorder the delimiters by input numbers. For example, if each message of you file starts from a timestamp, the order number of component 'Timestamp' should be set to 1
  - choose timestamp format used by your chat file
  - enable 'Skip First Line' if the first line of your chat log is a title
- **Customise keywords**
![screenshot of suite selection page](image-4.png)
  - messages with keywords would be highlighted in the analysis
  - keywords are grouped into suites
  - selected suites would be applied to the file analysis
  - add keywords to suites and assign risk factors
  - risk factors ranges from 0-10
  - keywords with risk factor = 0 wouldn't show up in analysis, might be useful if you want to disable some keywords temporarily
  - Person and Locations are identified by SpaCy models by default. Turn on 'Use ChatGPT for analysis' if you'd like ChatGPT to do it instead
- **File Management**
![screenshot of homepage](image-2.png)
  - double click on file to rename it
  - delete file by clicking '×' button to the right of the file name
  - search for file names using the search bar
  - files are ordered by upload date
- **More settings**
![screenshot of settings page](image-3.png)
  - access settings with the 'setting' button at the right end of the navigation bar
  - you could update keywords in settings, as well as in the process of upload file
  - 'Detection' section allow you to adjust thresholds for risk detection
  - 'Strictness' accounts for the threshold are message is marked as risky
  - setting 'Strictness' to 'Off' would disable message risk calculation
  - 'Sentiment' controls the impact of sentiment analysis in message risk calculation
  - setting 'Sentiment' to 'Off' would disable sentiment analysis in risk calculation process
- **Content Review**
![scrrenshot of content review page](image-6.png)
  - sender, message content will be shown on the left side
  - 'Regenerate' allows to re-analyse the file with different keywords, GPT and strictness settings
  - 'Download XML' generates XML files for the analysis, i.e. everything on the right side of the page
  - 'Restore' button un-applies all filters
  - 'Summarise' asks ChatGPT to summarise the chat for you (to use this feature, an OpenAI key need to be provided first, see 'Step 4 add .env' in README.md and 'GPT troubleshooting' section for details)
  - buttons in 'Risk Level' section filters messages based on calculated risk for each message
  - hover on buttons in 'Person' and 'Location' highlights them in the chat, and clicking on them filters out messages containing them for you
  - use 'Date/Time Filter' to view messages in a certain period
  - 'Visualisation' shows a graph Plotting each participant's message length against timeline
- **Get help from ChatGPT**
![screenshot of GPT page](image-7.png)
  - start a chat with GPT by clicking on 'New ChatGPT' button from an analysis
  - if you want to talk about messages in a certain time period, filter messages by Date/Time on content review page before starting a new chat. Currently applied Date/Time filter is shown at the top right of the chat window.
  - 'Existing ChatGPT' shows the chat you already started with ChatGPT
  - there's a list of prompts on the right to make things easier
  - past chats are listed on the left hand side
  - double click on chats to rename them
  - search chats with their names
  - 'Go to file' button brings you back to the analysis
- **GPT troubleshooting**
  - if you are getting 'An error occurred: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable', please double check if you have .env set up in the correct folder
  - if you are getting errors like:  OpenAI API returned an API Error: Error code: 401 - {'error': {'message': 'Incorrect API key provided: <your api key> You can find your API key at https://platform.openai.com/account/api-keys.', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_api_key'}}, please double check the key you provided in .env is correct and try restart the server


