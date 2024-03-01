# PSoP, the Discord Chatbot
**This project is now abandoned! This was pretty much made as a joke, the bot also can't be invited anymore, max discord guilds were reached :(**

The public PSoP Github repository. It uses the BeautifulSoup (bs4), requests, discord.py, pymysql and python-dotenv libraries.

If you are looking forward on using the bot and newer pokemons are released, you will need to edit the 'maxNum' variable located in 'settings.py', and add all the values into the MySQL database. Those being manually inserted or with a script.

Enjoy! (Please, credit me if you use the source code in any way).

## How to use for yourself?
~~If you'd like to skip this entirely, you can invite the always 24/7 bot that can be found by clicking here~~. 

~~Alternatively, you can follow the steps below to self-host the bot. (I don't recommend this at all)~~ (This is no longer supported.)
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
It'll probably wont be fixed! (sorry, not sorry.)

### How can I create a SQL database?
You can use Amazon AWS, Google Cloud, Firebase... They have some great tutorials on how to get started!

### Some Pokemon arent shown/I want to hide newer gen Pokemon.
There is a hard-cap on the pokemon ID, you can see it in the file "settings.py" and change it to your liking.

### Where do I download the bot?
Click [here](https://github.com/xUnderGame/PSoP/releases/tag/v4.1.0) to download the lastest release of this bot.
