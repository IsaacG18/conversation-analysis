# Conversation analyst

To get this code running require steps for set up

# Step 1 install python and pip
You need to have Python 3.11 installed on your system. If you haven't installed it yet, you can download it from the [official Python website](https://www.python.org/downloads/) and follow the installation instructions for your operating system.

To verify if pip is installed, you can run the following command in your terminal or command prompt:

    pip --version


# Step 2 clone the repo

    git clone https://github.com/IsaacG18/conversation-analysis.git

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

Current version is gpt-3.5-turbo
If the key needs updated the .env and re-run Step 7

# Step 5 install packages
File path: conversation-analysis/
**Using Init Script**
You can skip Step 5 and 6 using

    chmod +x init.sh

    ./init.sh

Or for windows

    init.bat

**For manual install:**
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

To run the file 100 times do this

    time (for i in {1..100}; do python speed_test_messages.py; done)

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
Available from the 14th of March, available as github and website
- Visual updates
  - Content Review Page
  - ChatGPT page
  - Waiting message for data analysis 
- New features
  - ChatGPT summary
  - Search bar on chatgpt page
  - Allow the renaming of chats
  - Customsation of risk levels
  - Increased naviation between chatgpt page and content review
  - Allow chatgpt to find names and locations
  - Ability to delete old analysis
  - Ability to select to skip a line as title line
- Other improvements
  - Cleaner code
  - Increase testing
  - Bug fixes on display html in chats
  - Filter out emojis from names
  - Less files stored on machine

# Application Overview
**HomePage**:
This is the main page which displays all of your uploaded files.

 - There is a search bar at the top right hand side that can be  used to filter through your uploaded files by name.
 - Next to the search bar there is three buttons : Upload File, Setttings, and ChatGBT.
 - Clicking on an uploaded file will lead you to the analysis page. These files can also be deleted if the "x" icon is pressed.
 - Double clicking on an uploaded file will allow you to rename it.
 - Clicking to "Conversation Analyst" on the top left hand side will always lead the user back to the home page.

**Analysis Page**:
The app uses Natural Language Processing (NLP) to analyse text documents and generate reports.

- The system then processes the document and displays key information.
- Filtering on this page only works one at the time.
- What is analysed:
  - Names
  - Locations
  - Custom Inputed Keyword (Lemmas of each words)
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

- Suites and keywords risk factor are used to filter results based upon their level. The higher the number the more risky the keyword.
- After successfully uploading a file user will be redirected to the analysis page.

**Settings Page**:
Keywords and Detection settings can be customized here.

- In keyword tab, suites and keywords can be added and removed
- In detection tab, the level of strictness and sentiment and be adjusted from high to low
  - This adjustment can range from high to low, offering a balance between precision and recall based on the user's preference or requirements for the analysis.
  - Users can tweak how sentiment analysis is conducted. This may involve adjusting the sensitivity of the sentiment analysis tool, enabling the application to more accurately reflect the tone and mood of the conversations being analyzed.

**ChatGBT Page**:
This page  allows you to interact with the AI model directly. Suggested prompts are also offered.

- You can type in any message and get suggestions for what to say next.
- When messages are parsed they are only filtered by time.
- Search bar to filter through chat history.
- Multiple conversation can be made simultaneously.
- Conversations can be renamed by double clicking them.