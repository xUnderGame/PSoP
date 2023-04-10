import asyncio
import os
import random
import re
from urllib import error, request

import interactions
import pymysql
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import dotenv_values

import settings

# Defining Client.
_ready: bool = False
intents = interactions.Intents.ALL
client = interactions.Client(token=dotenv_values()["BOT_TOKEN"],intents=intents)


# On ready event.
@client.event
async def on_ready():
    global _ready
    if not _ready:
        # await client.change_presence(interactions.ClientPresence(activities=[interactions.PresenceActivity(name="sp!help | pokemon.com", type=interactions.PresenceActivityType.GAME)]))
        global botIcon, pokemon, user, db
        botIcon = settings.botIcon

        # Prints and databases
        print("====== Bot Stats ======")
        print(" > Logged in as:", str(client.me.name))
        print(" > Latency: " + str(client.latency)[0:4] + "ms")
        print("====== App Stuff ======")

        # Connect to the database.
        dbConnect()
        try:
            if db:
                print("Database loaded correctly!")
        except:
            print("No DB detected, commands will not update/fetch from the database.")
            db = None
            pass
        _ready = True


# Help Command.
@client.command(
    name = "help",
    description = "Lists all of the bot's commands.",
    scope = 771651788134547456
)
async def help(ctx: interactions.CommandContext):
    embed = makeEmbed(ctx, "PSoP Commands", "`help`, `check`, `smash`, `pass`, `preferences`, `stats`, `potd`, `top`, `info`, `repo`")
    await ctx.send(embeds=embed)


# Info command.
@client.command(
    name = "info",
    description = "Shows information about this bot.",
    scope = 771651788134547456
)
async def info(ctx: interactions.CommandContext):
    embed = makeEmbed(ctx, "Information", "Thank you for adding the bot! This is one of my small projects, and I plan to keep on updating this semi-regularly.\nIf you'd like to check it out, you can use the `repo` command to see the source code.\nBot was made so it uses [requests](https://pypi.org/project/requests), [pymysql](https://pypi.org/project/PyMySQL) and [bs4](https://pypi.org/project/beautifulsoup4) to access the images from the [pokemon.com](https://pokemon.com/pokedex) pokedex. This was made in python by **UnderGame#4540**. Feel free to contact me, and I hope you have fun!")
    embed.add_field(name="Commands Information",
                    value=f"Almost all commands accept the Pokemon **ID**, the **name** and '**random**' as arguments. That way, you can find your desired pokemon easily.",
                    inline=True)
    await ctx.send(embeds=embed)


# Repository command.
@client.command(
    name = "repo",
    description = "Sends back the repository of this bot. It's open source!",
    scope = 771651788134547456,
)
async def repo(ctx: interactions.CommandContext):
    embed = makeEmbed(ctx, "Github Repo", "Check out the github repository [here](https://github.com/xUnderGame/PSoP)! If you wish to join the support discord, feel free to do so by clicking [here](https://discord.com/invite/Az7skvA2mf).")
    await ctx.send(embeds=embed)


# Preferences command.
@client.command(
    name="preferences",
    description="Change your bot settings with this command.",
    scope=771651788134547456,
    options=[
        interactions.Option(
            name="favorite",
            description="Change your favourite pokemon!",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="number",
                    description="The pokemon number.",
                    type=interactions.OptionType.INTEGER,
                    required=False
                )
            ]
        ),
        interactions.Option(
            name="previous",
            description="Toggle on/off the ability to see previously seen pokemons.",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="toggle",
                    description="Insert a bool (true/false) to toggle this setting.",
                    type=interactions.OptionType.BOOLEAN,
                    required=True
                )
            ]
        )
    ]
)
async def preferences(ctx: interactions.CommandContext, sub_command: str, toggle: bool = False, number: int = random.randrange(1, settings.maxNum+1)):
    notImplemented = "(Not implemented as of now)"

    # Check if a database is up and working.
    if not db:
        await ctx.send("Sorry, we aren't able to load the database right now. Try again later!")
        return
    
    # Set the user's new favorite pokemon.
    if sub_command == "favorite":
        # Check if the change is valid.
        number, editEmbed = await checkPokeNum(str(number), ctx, False)
        if not number:
            badEmbed = makeEmbed(ctx, "Preferences Error!", "Invalid pokemon number entered, check your arguments and try again.")
            await ctx.send(embeds=badEmbed)
            return

        # Updates the user's fav pokemon.
        dbUpdateFav(ctx, number)
        favEmbed = makeEmbed(ctx, "Favorites Updated", f"Your new favorite pokemon has been set to {number}!")
        await editEmbed.edit(embeds=favEmbed)

    # Toggles viewing recently seen pokemons.
    elif sub_command == "previous":
        # Change the setting.
        if not toggle:
            prevEmbed = makeEmbed(ctx, "Setting Updated", f"You will no longer see recent pokemons when using the random parameter. {notImplemented}")
            dbUpdatePrev(ctx, False)
        elif toggle:
            prevEmbed = makeEmbed(ctx, "Setting Updated", f"You will now start to see recent pokemons when using the random parameter. {notImplemented}")
            dbUpdatePrev(ctx, True)
        
        await ctx.send(embeds=prevEmbed)


# Fav user poke command & stats.
@client.command(
    name = "stats",
    description = "Shows your stats with the bot. Command usage and more!",
    scope = 771651788134547456
)
async def stats(ctx: interactions.CommandContext):
    # Check if a database is up and working.
    if not db:
        await ctx.send("Sorry, we aren't able to load the database right now. Try again later!")
        return
    
    # Get the information needed.
    smashPass = dbGetUserSmashPass(ctx)
    favPokeNum = str(checkPokeImage(str(dbGetFavPoke(ctx)[0])))

    # Embed.
    statsEmbed, pokeImage = makeEmbed(ctx, f"{ctx.author.name}'s Stats.", "Take a look at your personal stats and cool info about your time with the bot! (Favourite Pokemon is randomized once if unset.)", favPokeNum)
    statsEmbed.add_field(name="Total Smashed", value=f"{smashPass[0][0]} Pokemons smashed. (All time)", inline=True)
    statsEmbed.add_field(name="Total Passed", value=f"{smashPass[0][1]} Pokemons passed. (All time)", inline=True)
    statsEmbed.add_field(name="Favourite Pokemon", value=f"Your favourite Pokemon is {favPokeNum}.", inline=True)
    await ctx.send(files=pokeImage, embeds=statsEmbed)


# Leaderboard command. Shows the top x most smashed pokemon.
@client.command(
    name = "leaderboard",
    description = "Replies back with a leaderboard containing the most smashed pokemons number.",
    scope = 771651788134547456
)
async def leaderboard(ctx: interactions.CommandContext):
    # Get the information needed.
    hardCap = 9
    leaderboard = dbGetLeaderboard(hardCap)
    highestPoke = str(checkPokeImage(leaderboard[0][0]))

    # Prepare embed and send.
    leaderEmbed, pokeImage = makeEmbed(ctx, "Most smashed", f"Here's a list of the {hardCap} most smashed pokemons of all time. Due to limitations, right now we can only show the pokemon number. This will be changed in the future.", highestPoke)
    for poke in leaderboard:
        leaderEmbed.add_field(name=f"{poke[0]}", value=f"Was smashed a total of {poke[1]} times.", inline=True)
    await ctx.send(files=pokeImage, embeds=leaderEmbed)


# Pokemon of the day command.
@client.command(
    name = "potd",
    description = "Sends the pokemon of the day!",
    scope = 771651788134547456,
)
async def potd(ctx: interactions.CommandContext):
    # Calculate the pokemon of the day and send it. (Day + Month + first two digits of the year + third digit + fourth)
    cDate = datetime.now()
    day = cDate.day
    month = cDate.month
    year = str(cDate.year)

    # Call check() to do the usual stuff.
    total = day + month + int(year[0]+year[1]) + int(year[2]) + int(year[3])
    await check(ctx, str(total))


# Smash command
@client.command(
    name = "smash",
    description = "Smash a pokemon of your choosing.",
    scope = 771651788134547456,
    options=[
        interactions.Option(
            name="number",
            description="The pokemon number.",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def smash(ctx: interactions.CommandContext, number: str = "random"):
    # Check for the number
    number, deleteEmbed = await checkPokeNum(number, ctx, True)
    if number is False:
        return

    # Checks if the image is already downloaded.
    number = str(number)
    number = checkPokeImage(number)

    # Get pokemon info.
    htmlSouped = getWebsite(number)
    pokeName = getPokeName(htmlSouped)
    pokeDesc = getPokeDesc(htmlSouped)

    # Times Smashed/Passed + add the user entry.
    dbSmashPass(number, "smashed", ctx)
    dbPokeLoad(number)
    wouldSmash = pokemon[1]
    wouldPass = pokemon[2]

    # Get the color of the embed.
    statusColor = await getColoredEmbed(htmlSouped)

    # Prepare and send the embed with the image.
    statusEmbed, pokeImage = makeEmbed(ctx, pokeName, f"Description: {pokeDesc}", number, statusColor)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldSmash}` users would now SMASH this pokemon.", inline=True)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldPass}` users would pass this pokemon.", inline=True)
    statusEmbed.add_field(name="Smashed!", value=f"You would smash this pokemon, heck yeah.", inline=False)
    statusEmbed.set_footer(icon_url=botIcon, text="PSoP, version 4.1")
    await deleteEmbed.delete()
    await ctx.send(files=pokeImage, embeds=statusEmbed)


# Pass command.
@client.command(
    name = "pass",
    description = "Pass a pokemon of your choosing.",
    scope = 771651788134547456,
    options=[
        interactions.Option(
            name="number",
            description="The pokemon number.",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def pokePass(ctx: interactions.CommandContext, number: str = "random"):
    # Check for the number.
    number, deleteEmbed = await checkPokeNum(number, ctx, True)
    if number is False:
        return

    # Checks if the image is already downloaded.
    number = str(number)
    number = checkPokeImage(number)

    # Get pokemon info.
    htmlSouped = getWebsite(number)
    pokeName = getPokeName(htmlSouped)
    pokeDesc = getPokeDesc(htmlSouped)

    # Times Smashed/Passed + add the user entry.
    dbSmashPass(number, "passed", ctx)
    dbPokeLoad(number)
    wouldSmash = pokemon[1]
    wouldPass = pokemon[2]

    # Get the color of the embed.
    statusColor = await getColoredEmbed(htmlSouped)

    # Prepare and send the embed with the image.
    statusEmbed, pokeImage = makeEmbed(ctx, pokeName, f"Description: {pokeDesc}", number, statusColor)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldSmash}` users would SMASH this pokemon.", inline=True)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldPass}` users would now pass this pokemon.", inline=True)
    statusEmbed.add_field(name="Passed!", value=f"You wouldn't smash this pokemon. That's good.", inline=False)
    statusEmbed.set_footer(icon_url=botIcon, text="PSoP, version 4.1")
    await deleteEmbed.delete()
    await ctx.send(files=pokeImage, embeds=statusEmbed)


# Check command.
@client.command(
    name = "check",
    description = "placeholder",
    scope = 771651788134547456,
    options=[
        interactions.Option(
            name="number",
            description="The pokemon number.",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def check(ctx, number: str = "random"):
    # Check for the number.
    number, deleteEmbed = await checkPokeNum(number, ctx, True)
    if number is False:
        return

    # Checks if the image is already downloaded.
    number = str(number)
    number = checkPokeImage(number)

    # Open page and stuff.
    htmlSouped = getWebsite(number)

    # Let's find the Pokemon information...
    pokeName = getPokeName(htmlSouped)
    pokeDesc = getPokeDesc(htmlSouped)
    pokeGender = getPokeGenders(htmlSouped)
    pokeCategory = getPokeCategory(htmlSouped)
    pokeHeight = getPokeHeight(htmlSouped)
    pokeWeight = getPokeWeight(htmlSouped)

    # Times Smashed/Passed.
    dbPokeLoad(number)
    wouldSmash = pokemon[1]
    wouldPass = pokemon[2]

    # Get the color of the embed.
    statusColor = await getColoredEmbed(htmlSouped)

    # Prepare the buttons.
    buttons =[
        interactions.ActionRow( # https://discord.com/developers/docs/resources/emoji#emoji-object
            components=[
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    label="Smash",
                    custom_id="smash"
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.DANGER,
                    label="Pass",
                    custom_id="pass"
                )
            ]
        )
    ]

    # Prepare and send the embed with the image.
    statusEmbed, pokeImage = makeEmbed(ctx, pokeName, f"Description: {pokeDesc}", number, statusColor)
    statusEmbed.add_field(name="Gender", value=f"{pokeGender}", inline=True)
    statusEmbed.add_field(name="Height", value=f"{pokeHeight}", inline=True)
    statusEmbed.add_field(name="Weight", value=f"{pokeWeight}", inline=True)
    statusEmbed.add_field(name="Category", value=f"{pokeCategory}", inline=True)
    statusEmbed.add_field(name="Times Smashed", value=f"`{wouldSmash}` users would SMASH.", inline=True)
    statusEmbed.add_field(name="Times Passed", value=f"`{wouldPass}` users would pass.", inline=True)
    await deleteEmbed.delete()
    pokeEmbed = await ctx.send(files=pokeImage, embeds=statusEmbed, components=buttons)

    # Reaction Time.
    try:
        def buttonCheck(button, user):
            return button.message.id == pokeEmbed.id and button.custom_id in ["smash", "pass"] and user == ctx.author
    
        btn, user = await client.wait_for(
            "button_click",
            check = buttonCheck,
            timeout=30.0
        )

        if btn.custom_id == "smash":
            await ctx.send(content="smashed", ephemeral=False)
        else:
            await ctx.send(content="passed", ephemeral=False)
        
        # Check if more people reacted to the message.
        # extraEmbed = ""
        # if reactionUsed[0].count > 2:
        #     extraEmbed = f"and {reactionUsed[0].count-2} people "

        # # Smash or pass thing.
        # if reactionUsed[0].emoji == "👊":
        #     statusEmbed.add_field(name=f"👊 You {extraEmbed}would SMASH that pokemon!",
        #                           value="Your choice has been saved into the database.", inline=True)
        #     dbSmashPass(number, "smashed", ctx)

        # elif reactionUsed[0].emoji == "💔":
        #     statusEmbed.add_field(name=f"💔 You {extraEmbed}would pass that pokemon.",
        #                           value="Your choice has been saved into the database.", inline=True)
        #     dbSmashPass(number, "passed", ctx)

    # Timeout, do nothing.
    except asyncio.TimeoutError:
        statusEmbed.add_field(
            name="Timed out", value=f"Reacting won't do anything anymore.", inline=True)

    # Edit the thing
    await pokeEmbed.edit(embeds=statusEmbed)


# Makes an embed with the given parameters.
def makeEmbed(ctx, title: str, description: str, imageNum: str=None, statusColor=settings.defaultColor):
    embed = interactions.Embed(title=title, description=description,
                              timestamp=ctx.created_at, color=statusColor)
    embed.set_footer(icon_url=botIcon, text="PSoP, version 5.0")
    
    # Check if we want an image.
    if imageNum:
        image = interactions.File(filename=f"./images/{imageNum}.png", description="A Pokemon!")
        embed.set_thumbnail(url=f"attachment://{imageNum}.png")
        return embed, image
    
    return embed


# Adds a zero to the start of the number, to not get a 404 request.
def addZeroLeft(number):
    return "0"+number


# Fetches the website and parses it, returning it.
def getWebsite(number):
    pokeUrl = str("https://www.pokemon.com/us/pokedex/" + number)  # The URL we are using.
    pokeRequest = requests.get(pokeUrl, headers={"User-Agent": "Mozilla/5.0"})  # Requests access.
    # Parses the ENTIRE page and returns it
    return BeautifulSoup(pokeRequest.text, 'html.parser')


# Checks the Pokémon image.
def checkPokeImage(number: str):
    if int(number) < 100 and len(number) < 3:
        number = addZeroLeft(number)
    # Check if the image already exists, and so we don't download it again.
    fileCheck = os.path.exists("images/" + str(number) + ".png")
    if fileCheck is False:
        # Do the request. (And download the file locally)
        requestedUrl = str("https://assets.pokemon.com/assets/cms2/img/pokedex/full/" + str(number) + ".png")
        request.urlretrieve(requestedUrl, "images/" + str(number) + ".png")
    return number


# Get the Pokémon name.
def getPokeName(htmlSpoon):
    pokeName = ""

    # Let's find the Pokémon name!
    # Finds the specific class.
    spoonedDiv = htmlSpoon.find('div', {"class": "pokedex-pokemon-pagination-title"})

    # Fiddle with rawString
    try:
        # Gets the text from the specific class.
        rawString = str(spoonedDiv.text)
        rawString = rawString.replace("\n", "")  # Removes newlines.
        pokeList = rawString.split()  # Splits it into a list.
        for num in range(len(pokeList)):  # Iterates in the list.
            # Adds the names together, useful if the Pokémon has more than one name.
            pokeName = pokeName + pokeList[num]
            return pokeName
    except AttributeError:
        raise error


# Get the Pokémon description.
def getPokeDesc(htmlSpoon):
    # Let's find the pokemon description...
    spoonedDiv = htmlSpoon.find('p', {"class": "version-x"})

    # Fiddle with rawString.
    rawString = str(spoonedDiv.text)
    pokeDesc = rawString.lstrip()
    return pokeDesc


# Get the pokemon genders.
def getPokeGenders(htmlSpoon):
    # Lets find the pokemon genders...
    pokeGender = "None"
    doMale = False
    doFemale = False
    if htmlSpoon.find_all("i", {'class': {'icon_male_symbol'}}):
        doMale = True
    if htmlSpoon.find_all("i", {'class': {'icon_female_symbol'}}):
        doFemale = True

    # Check for genders.
    if doMale is True and doFemale is False:
        pokeGender = ":male_sign: Male"
    elif doFemale is True and doMale is True:
        pokeGender = ":transgender_symbol: Male, Female"
    elif doFemale is True and doMale is False:
        pokeGender = ":female_sign: Female"
    elif doFemale is False and doMale is False:
        pokeGender = ":grey_question: Unknown"
    return pokeGender


# Get the Pokémon category.
def getPokeCategory(htmlSpoon):
    # Let's find the pokemon category...
    spoonedDiv = htmlSpoon.find(
        'div', {"class": ["pokemon-ability-info", "match", "color-bg"]})
    rawString = str(spoonedDiv.text)
    pokeRegex = rawString.replace("\n", "")
    abilityCount = int(pokeRegex.lower().count('abilities'))

    # Fiddle with rawString
    if abilityCount > 1:
        pokeCategory = ":warning: Cannot load."
    else:
        pokeCategory = re.search('Category(.*)Abilities', pokeRegex)
        pokeCategory = str(pokeCategory.group(1))
    return pokeCategory


# Get the Pokémon height.
def getPokeHeight(htmlSpoon):
    # Let's find the pokemon height...
    spoonedDiv = htmlSpoon.find('div', {"class": {"column-7"}})
    rawString = str(spoonedDiv.text)
    pokeRegex = rawString.replace("\n", "")

    # Fiddle with rawString.
    pokeHeight = re.search('Height(.*)Weight', pokeRegex)
    pokeHeight = str(pokeHeight.group(1))
    return pokeHeight


# Get the Pokémon weight.
def getPokeWeight(htmlSpoon):
    # Let's find the pokemon weight...
    spoonedDiv = htmlSpoon.find('div', {"class": {"column-7"}})
    rawString = str(spoonedDiv.text)
    pokeRegex = rawString.replace("\n", "")

    # Fiddle with rawString. (Again, again, again, again...!)
    pokeWeight = re.search('Weight(.*)Gender', pokeRegex)
    pokeWeight = str(pokeWeight.group(1))
    return pokeWeight


# Check if the Pokémon number is correct.
async def checkPokeNum(pokeNum, ctx, doEmbed: bool = True):
    badNumber = False

    # Starting embed.
    processingEmbed = makeEmbed(ctx, "Processing Command...", "Please wait a couple of seconds.")
    processEdit = await ctx.send(embeds=processingEmbed)

    # Random number?
    if "random" in pokeNum.lower():
        pokeNum = str(random.randint(1, settings.maxNum))

    # Check if the number is valid.
    if pokeNum.isdigit():
        pokeNum = int(pokeNum)
        if pokeNum > settings.maxNum or pokeNum < 1:
            badNumber = True

    # Number length and stuff.
    if len(str(pokeNum)) > 0 and len(str(pokeNum)) < 5 and not str(pokeNum).isdigit() and badNumber is not True:
        badNumber = True

    # Check if not 404.
    if not badNumber:
        pokeNum = str(pokeNum)
        requestedUrl = str("https://www.pokemon.com/us/pokedex/" + pokeNum)
        try:
            _connTest = request.urlopen(requestedUrl)
        except error.HTTPError as e:
            msgTimestamp = str(ctx.message.created_at)
            msgTimestamp = msgTimestamp[11:19]
            print(">> HTTP Error: " + str(e.code) + " || Pokemon: " +
                  pokeNum + " || Timestamp: " + msgTimestamp + " <<")
            badNumber = True

    # Get the number if it's a valid string.
    if not badNumber and not pokeNum.isdigit():
        htmlSouped = getWebsite(pokeNum)
        spoonedDiv = htmlSouped.find('div', {"class": "pokedex-pokemon-pagination-title"})  # Finds the specific class.
        try:
            # Finds the specific class
            spoonedDiv = spoonedDiv.find('span', {"class": "pokemon-number"})

            # Gets the text from the specific class.
            rawString = str(spoonedDiv.text)
            rawString = rawString.replace("\n", "")  # Removes newlines.
            pokeNum = str(rawString[1:])
        except:
            badNumber = True

    # If bad then exit.
    if badNumber:
        if doEmbed: 
            errorEmbed = makeEmbed(ctx, "Error!", ":x: Sorry, we couldn't find that Pokemon! It might be a server issue or the Pokemon does not exist. You should use '-' if the Pokemon is separated by spaces.")
            await processEdit.edit(embeds=errorEmbed)
        return False, processEdit
    else:
        if doEmbed:
            # Pokémon was found!
            goodEmbed = makeEmbed(ctx, "Pokemon Found!", ":white_check_mark: Loading the pokemon now.")
            await processEdit.edit(embeds=goodEmbed)

        pokeNum = str(pokeNum)
        return pokeNum, processEdit


# Colored embed definition.
async def getColoredEmbed(htmlSpoon):  # pokedex-pokemon-attributes.
    spoonedDiv = htmlSpoon.find('div', {"class": "dtm-type"})

    # Cases wouldn't work here for some reason, cover your eyes!
    if spoonedDiv.find_all("li", {"class": "background-color-fire"}):
        return 0xE04938
    elif spoonedDiv.find_all("li", {"class": "background-color-water"}):
        return 0x327CED
    elif spoonedDiv.find_all("li", {"class": "background-color-grass"}):
        return 0x27D855
    elif spoonedDiv.find_all("li", {"class": "background-color-electric"}):
        return 0xE2E051
    elif spoonedDiv.find_all("li", {"class": "background-color-bug"}):
        return 0x6BAD58
    elif spoonedDiv.find_all("li", {"class": "background-color-flying"}):
        return 0xAFCECB
    elif spoonedDiv.find_all("li", {"class": "background-color-rock"}):
        return 0xBC8824
    elif spoonedDiv.find_all("li", {"class": "background-color-ice"}):
        return 0x6AE5E7
    elif spoonedDiv.find_all("li", {"class": "background-color-poison"}):
        return 0xA95CDF
    elif spoonedDiv.find_all("li", {"class": "background-color-psychic"}):
        return 0xE036D9
    elif spoonedDiv.find_all("li", {"class": "background-color-normal"}):
        return 0x898989
    elif spoonedDiv.find_all("li", {"class": "background-color-dark"}):
        return 0x746184
    elif spoonedDiv.find_all("li", {"class": "background-color-dragon"}):
        return 0x0C83C6
    elif spoonedDiv.find_all("li", {"class": "background-color-fairy"}):
        return 0xB93AA9
    elif spoonedDiv.find_all("li", {"class": "background-color-ghost"}):
        return 0x64347F
    elif spoonedDiv.find_all("li", {"class": "background-color-ground"}):
        return 0x7F5E34
    elif spoonedDiv.find_all("li", {"class": "background-color-steel"}):
        return 0x6B6E80
    elif spoonedDiv.find_all("li", {"class": "background-color-fighting"}):
        return 0xDC812C
    return 0x6338E1


# Connect to the database.
def dbConnect():
    global db
    try:
        db = pymysql.connect(host=dotenv_values()["DB_HOST"],
                             user=dotenv_values()["DB_UNAME"],
                             password=dotenv_values()["DB_PASS"],
                             database=dotenv_values()["DB"],
                             autocommit=True)
    except:
        pass


# Check if the user exists
def dbCheckUser(ctx):
    if db and db.open:
        with db.cursor() as cursor:
            updateQuery = f"SELECT id FROM USERS WHERE id = {int(ctx.author.id)}"
            cursor.execute(updateQuery)
            searchResult = cursor.fetchone()
            if not searchResult:
                dbCreateUser(ctx)

# Creates a row into USER with the user's information & generates a random favPoke entry.
def dbCreateUser(ctx):
    if db and db.open and ctx:
        with db.cursor() as cursor:
            updateQuery = f"INSERT INTO USERS (id, favPoke) VALUES ({int(ctx.author.id)}, {random.randrange(1, settings.maxNum+1)})"
            cursor.execute(updateQuery)


# Updates the favPoke entry. (Leave empty for a random pokemon)
def dbUpdateFav(ctx, favPoke: int = random.randrange(1, settings.maxNum+1)):
    if db and db.open and ctx:
        with db.cursor() as cursor:
            updateQuery = f"UPDATE USERS SET favPoke = {favPoke} WHERE id = {int(ctx.author.id)}"
            cursor.execute(updateQuery)


# Updates the showPrev entry. (SEMI-UNUSED AS OF NOW)
def dbUpdatePrev(ctx, value: bool):
    if db and db.open and ctx:
        with db.cursor() as cursor:
            updateQuery = f"UPDATE USERS SET showPrev = {value} WHERE id = {int(ctx.author.id)}"
            cursor.execute(updateQuery)


# Update user into db.
def dbUserSmashPass(sop: str, ctx):
    if sop and ctx(sop == "smashed" or sop == "passed"):
        with db.cursor() as cursor:
            if sop.lower() == "smashed":
                updateQuery = f"UPDATE USERS SET smashed = smashed + 1 WHERE id = {int(ctx.author.id)}"
            elif sop.lower() == "passed":
                updateQuery = f"UPDATE USERS SET passed = passed + 1 WHERE id = {int(ctx.author.id)}"
            else:
                return
            cursor.execute(updateQuery)


# Loads the smashed and passed Pokémon from the MySQL db.
def dbPokeLoad(pokeNum: str):
    global pokemon

    # Check for a valid conenction and attempt to connect.
    if not db or not db.open:
        pokemon = (0, 0, 0)
        dbConnect()
        return
    if not pokeNum:
        pokemon = (0, 0, 0)
        return

    # Do the query
    with db.cursor() as cursor:
        selQuery = f"SELECT * FROM SP WHERE id = {int(pokeNum)}"
        cursor.execute(selQuery)
        pokemon = cursor.fetchone()


# Saves one of the user's choice into the MySQL db.
def dbSmashPass(pokeNum: str, sop: str, ctx):
    # Create an user?
    dbCheckUser(ctx)
    
    if db and db.open and pokeNum and (sop.lower() == "smashed" or sop.lower() == "passed"):
        with db.cursor() as cursor:
            # Add entry to SP table.
            if sop.lower() == "smashed":
                updateQuery = f"UPDATE SP SET smashed = smashed + 1 WHERE id = {int(pokeNum)}"
            elif sop.lower() == "passed":
                updateQuery = f"UPDATE SP SET passed = passed + 1 WHERE id = {int(pokeNum)}"
            else:
                return
            cursor.execute(updateQuery)

            # Update USERS smashed/passed.
            if sop.lower() == "smashed":
                updateQuery = f"UPDATE USERS SET smashed = smashed + 1 WHERE id = {int(ctx.author.id)}"
            elif sop.lower() == "passed":
                updateQuery = f"UPDATE USERS SET passed = passed + 1 WHERE id = {int(ctx.author.id)}"
            cursor.execute(updateQuery)


# Gets the smashed and passed count from an user.
def dbGetUserSmashPass(ctx):
    with db.cursor() as cursor:
        # Check if an user exists.
        updateQuery = f"SELECT id FROM USERS WHERE id = {int(ctx.author.id)}"
        cursor.execute(updateQuery)
        searchResult = cursor.fetchone()
        if not searchResult:
            dbCreateUser(ctx)

        selectQuery = f"SELECT smashed, passed FROM USERS WHERE id = {int(ctx.author.id)}"
        cursor.execute(selectQuery)
        return cursor.fetchall()


# Gets the fav pokemon from an user.
def dbGetFavPoke(ctx):
        with db.cursor() as cursor:
            selectQuery = f"SELECT favPoke FROM USERS WHERE id = {int(ctx.author.id)}"
            cursor.execute(selectQuery)
            return cursor.fetchone()


# Gets the leaderboard.
def dbGetLeaderboard(cap: int=9):
        with db.cursor() as cursor:
            selectQuery = f"SELECT id, smashed FROM SP ORDER BY smashed DESC LIMIT {cap}"
            cursor.execute(selectQuery)
            return cursor.fetchall()


# Gets the showPrev value. (UNUSED AS OF NOW)
def dbGetPrev(ctx):
    if db and db.open and ctx:
        with db.cursor() as cursor:
            updateQuery = f"SELECT showPrev FROM USERS WHERE id = {int(ctx.author.id)}"
            cursor.execute(updateQuery)
            return cursor.fetchone()

client.start()