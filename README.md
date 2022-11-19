# PSoP, the Discord Chatbot
The public "*Pokemon Smash or Pass*" Github repository. It uses the BeautifulSoup (bs4), requests, discord.py, pymysql and python-dotenv. 

If you are looking forward on using the bot, please note that this isn't supported for newer pokemons (**as of now, maximum is 905**), therefore you will need to edit the 'maxNum' variable located in 'settings.py'.

Enjoy! (Please, credit me if you use the source code in any way).

## How to use for yourself?
If you'd like to skip this entirely, you can invite the always 24/7 bot that can be found by [clicking here](https://top.gg/bot/942443498915909683). 

Alternatively, you can follow the steps below to self-host the bot.
```
Step 1: Download the repository files using the "CODE" tab and clicking on "Download ZIP" or selecting the link at the bottom of this page.

Step 2: Go to a folder and extract the ZIP contents inside.

Step 3: Enter the "self-host" folder and rename the "env.txt" file to ".env".

Step 4: On PHPMyAdmin (Your SQL database), choose a database, and click on the "import" button. From there, select the "SP.sql" file located in "self-host" and import it.

Step 5: Build your own bot on the discord developer portal, and grab the BOT TOKEN.

Step 6: Go back to the ".env" file and move it to the main folder (PSoP), now replace the values with your own. After you are done, you can safely delete the "self-host" folder.

Step 7: Invite the bot to your server using the OAUTH generator, located in the discord developer portal.

Step 8: Run main.py and have fun!
```

## FAQ
### [Something] is not working!
You can join the Discord support/development server by clicking [this link](https://discord.com/invite/Az7skvA2mf).

### How can I create a SQL database?
You can use Amazon AWS, Google Cloud, Firebase... They have some great tutorials on how to get started!

### Some Pokemon arent shown/I want to hide newer gen Pokemon.
There is a hard-cap on the pokemon ID, you can see it in the file "settings.py" and change it to your liking.

### Where do I download the bot?
Click [here](https://github.com/xUnderGame/PSoP/releases/tag/v3.0.0) to download the lastest version of this bot.
