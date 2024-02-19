# Conversation analyst

To get this code running require steps for set up

# Step 1 install python and pip

# Step 2 clone the repo

# Step 3 install packages
**Window OS:**

pip install -r win_requirements.txt

**Other OS:**

pip install -r requirements.txt


# Step 4 add .env

In tp3/tp3 **create a file** called **.env**

Add in the file
CHATGPT_API_KEY=<api-key>

# Step 5 run these commands
Create and run the migrations:
1. **python manage.py makemigrations**
2. **python manage,py migrate**

Run the populate script

3. **python date_format_populate.py**


# After set up to run the website uses this command
File path: cs39-main/tp3
**python manage.py runserver**
