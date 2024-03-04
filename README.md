# Conversation analyst

To get this code running require steps for set up

# Step 1 install python and pip
You need to have Python 3.9 installed on your system. If you haven't installed it yet, you can download it from the [official Python website](https://www.python.org/downloads/) and follow the installation instructions for your operating system.

To verify if pip is installed, you can run the following command in your terminal or command prompt:
    --pip version


# Step 2 clone the repo

# Step 3 set up venv

    pip install virtualenv

Navigate to your project directory in the terminal or command prompt and run the following command to create a virtual environment named 'ca':


    virtualenv ca

**On Windows:**


    ca\Scripts\activate

**On macOS and Linux:**

    source venv/bin/activate


# Step 4 install packages

    pip install -r requirements.txt


# Step 5 run these commands
Create and run the migrations:

    python manage.py makemigrations
    
    python manage,py migrate
    
    python manage,py migrate --run-syncdb

Run the populate script

    python date_format_populate.py


# After set up to run the website uses this command
File path: cs39-main/tp3

    python manage.py runserver

