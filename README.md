# Conversation analyst

To get this code running require steps for set up

# Step 1 add .env

In tp3/tp3 create a file called .env

Add in the file
CHATGPT_API_KEY=<api-key>

# Step 2 run these commands

python manage.py makemigrations
python manage,py migrate
python date_format_populate.py

# After set up to run the website uses this command

python manage.py runserver