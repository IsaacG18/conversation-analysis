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