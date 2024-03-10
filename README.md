# Conversation analyst

To get this code running require steps for set up

# Step 1 install python and pip
You need to have Python 3.9 installed on your system. If you haven't installed it yet, you can download it from the [official Python website](https://www.python.org/downloads/) and follow the installation instructions for your operating system.

To verify if pip is installed, you can run the following command in your terminal or command prompt:
    --pip version


# Step 2 clone the repo

    git clone https://github.com/mentos-team/MentOS.git

# Step 3 set up venv

    pip install virtualenv

Navigate to your project directory in the terminal or command prompt and run the following command to create a virtual environment named 'ca':


    virtualenv ca

**On Windows:**


    ca\Scripts\activate

**On macOS and Linux:**

    source venv/bin/activate


# Step 4 install packages
**Window OS:**

    pip install -r win_requirements.txt

**Other OS:**

    pip install -r requirements.txt


# Step 5 add .env

In tp3/tp3 **create a file** called **.env**

Add in the file

    CHATGPT_API_KEY=<api-key>

# Step 6 run these commands
Create and run the migrations:

    python manage.py makemigrations
    
    python manage,py migrate
    
    python manage,py migrate --run-syncdb

Run the populate script

    python date_format_populate.py


# After set up to run the website uses this command
File path: cs39-main/tp3

    python manage.py runserver

# To test the speed of the code run this in linux
    
    time python speed_test_messages.py


# Versions

  

**1.0.0**
Available from the 15th of January
Access original only on Python Anywhere

Core Feature:
- NLP
- - Sentiment Analysis (not integrated)
- - Added Visualization for messages
- - Keyword Identification
- - Name and Location identification
- Data ingestion
- - Basic Customization of File ingestion
- - Custom Keywords (only in settings)
- - Compatibility with csv, docs, and txt
- - Error Handling in upload
- Front End
- - Search homepage for files
- - Word highlighting in content review
- - Date Filtering 
- - Key Highlighting
- ChatGPT
- - Nothing Implemented
  
**2.0.0**
Available from the 15th of February, available as github and website
- Content Review New features
- - Google Maps API search
- - Export XML data
- - Add re-analysis of file
- ChatGPT new features
- - Added the ability to message chatgpt
- - Added ability to create new chats
- - Added ability to access old chats
- - Added suggested prompts based on analysis
- Other new features
- - Renaming analysis on homepage
- Improvements to existing features
- - Search for root words in analysis
- - Improved customization in file structure including; dates, types order, and ability to added extra delimiters

**3.0.0**
Available from the 15th of March, available as github and website
- Visual updates
- - Content Review Page
- - ChatGPT page
- - Waiting message for data analysis 
- New features
- - ChatGPT summary
- - Search bar on chatgpt page
- - Allow the renaming of chats
- - Customsation of risk levels
- - Increased naviation between chatgpt page and content review
- - Allow chatgpt to find names and locations
- - Ability to delete old analysis
- Other improvements
- - Cleaner code
- - Increase testing
- - Bug fixes on display html in chats
- - Filter out emojis from names
- - Less files stored on machine