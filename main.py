import discord
import pymysql
import settings
import requests
import random
import asyncio
import re
import os

from dotenv import dotenv_values, load_dotenv
from discord.ext import commands
from bs4 import BeautifulSoup
from urllib import request
from urllib import error

# Defining Client
intents = discord.Intents.all()
client = commands.Bot(command_prefix="sp!", help_command=None, case_insensitive=True, intents=intents)

# ENV
load_dotenv()
config = dotenv_values(".env")


def __init__(self, client):
    self.client = client


# On ready event
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("sp!help | pokemon.com"))
    global botIcon
    global smashed
    global passed
    botIcon = settings.botIcon

    # Prints and databases
    print("====== Bot Stats ======")
    print(" > Logged in as:", str(client.user.name) + "#" + str(client.user.discriminator))
    print(" > Latency: " + str(client.latency)[0:4] + "ms")
    print("==== SQL Database ====")

    # Connect to the database
    global db
    db = pymysql.connect(host=dotenv_values()["DB_HOST"],
                         user=dotenv_values()["DB_UNAME"],
                         password=dotenv_values()["DB_PASS"],
                         database=dotenv_values()["DB"],
                         autocommit=True)
    if not db:
        print("No Database Detected, bot might crash.")
    else:
        print("Database loaded and working.")

    print("===== App Errors =====")


# Error handler
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(title="Error! (Member not Found)",
                              description="Sorry, it doesn't seem like that member exists.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Cooldown!",
                              description="Command on cooldown, you'll be able to use this command again in **{:.0f}s**".format(
                                  error.retry_after))
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Error! (Missing Argument)", description="Looks like you're missing an argument.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="Error! (Bad Argument)",
                              description="I didn't understand what you said, try again.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title="Error! (Permissions)", description="Sorry, not enough permissions!")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        raise error


# Help Command
@client.command(aliases=["prefix", "psop", "sop", "commands", "cmd"])
async def help(ctx):
    embed = discord.Embed(title="PSoP Commands", description="`help`, `check`, `smash`, `pass`, `info`, `repo`",
                          timestamp=ctx.message.created_at, color=settings.defaultColor)
    embed.set_footer(icon_url=botIcon, text="PSoP, version 3.0")
    await ctx.send(embed=embed)


# Info command
@client.command(aliases=["information", "credits"])
async def info(ctx):
    embed = discord.Embed(title="Information",
                          description="This bot was literally made in two days, and I'm not angry about how it looks, it's pretty decent.\nAnyways, all rights go to nintendo blah blah blah.\nThis bot is using requests and soup to access the images from the pokemon pokedex. Made in python by **UnderGame#4540**",
                          timestamp=ctx.message.created_at, color=settings.defaultColor)
    embed.add_field(name="Commands:",
                    value=f"All commands accept the Pokemon **ID**, the **name** and '**random**' as arguments. That way you can use them easily.",
                    inline=True)
    embed.set_footer(icon_url=botIcon, text="PSoP, version 3.0")
    await ctx.send(embed=embed)


# Repository command
@client.command(aliases=["repository", "git", "github", "code", "source"])
async def repo(ctx):
    embed = discord.Embed(title="Github Repo",
                          description="Check out the github repo [here](https://github.com/xUnderGame/PSoP)!",
                          timestamp=ctx.message.created_at, color=settings.defaultColor)
    embed.set_footer(icon_url=botIcon, text="PSoP, version 3.0")
    await ctx.send(embed=embed)


# Smash command
@client.command(aliases=["pokeSmash", "smashPoke", "pokemonSmash", "smashPokemon"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def smash(ctx, number: str):
    # Check for the number
    number, deleteEmbed = await checkPokeNum(number, ctx)
    if number is False:
        return

    number = str(number)
    # Check if the image already exists
    fileCheck = os.path.exists("images/" + number + ".png")
    if fileCheck is False:
        # Do the request (And download the file)
        requestedUrl = str("https://assets.pokemon.com/assets/cms2/img/pokedex/full/" + number + ".png")
        request.urlretrieve(requestedUrl, "images/" + number + ".png")

    # Open page and stuff
    pokeUrl = str("https://www.pokemon.com/us/pokedex/" + number)  # The URL we are using
    pokeRequest = requests.get(pokeUrl, headers={"User-Agent": "Mozilla/5.0"})  # Requests access
    htmlSouped = BeautifulSoup(pokeRequest.text, 'html.parser')  # Parses the ENTIRE page

    # Let's find the pokemon name...
    pokeName = getPokeName(htmlSouped)

    # Let's find the pokemon description...
    pokeDesc = getPokeDesc(htmlSouped)

    # Times Smashed/Passed + add the user entry
    updDB(number, "smashed")
    loadDB(number)
    wouldSmash = smashed
    wouldPass = passed

    # Get the color of the embed
    statusColor = await getColoredEmbed(htmlSouped)

    # Prepare and send the embed with the image
    fileToSend = discord.File("images/" + number + ".png", filename="pokemon.png")

    statusEmbed = discord.Embed(title=f"{pokeName}", description=f"Description: {pokeDesc}",
                                timestamp=ctx.message.created_at, color=statusColor)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldSmash}` users would now SMASH this pokemon.",
                          inline=True)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldPass}` users would pass this pokemon.", inline=True)
    statusEmbed.add_field(name="Smashed!", value=f"You would smash this pokemon, heck yeah.", inline=False)
    statusEmbed.set_thumbnail(url="attachment://pokemon.png")
    statusEmbed.set_footer(icon_url=botIcon, text="PSoP, version 3.0")
    await deleteEmbed.delete()
    await ctx.send(file=fileToSend, embed=statusEmbed)


# Pass command
@client.command(aliases=["pass", "passPoke", "pokemonPass", "passPokemon"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def pokePass(ctx, number: str):
    # Check for the number
    number, deleteEmbed = await checkPokeNum(number, ctx)
    if number is False:
        return

    number = str(number)
    # Check if the image already exists
    fileCheck = os.path.exists("images/" + number + ".png")
    if fileCheck is False:
        # Do the request (And download the file)
        requestedUrl = str("https://assets.pokemon.com/assets/cms2/img/pokedex/full/" + number + ".png")
        request.urlretrieve(requestedUrl, "images/" + number + ".png")

    # Open page and stuff
    pokeUrl = str("https://www.pokemon.com/us/pokedex/" + number)  # The URL we are using
    pokeRequest = requests.get(pokeUrl, headers={"User-Agent": "Mozilla/5.0"})  # Requests access
    htmlSouped = BeautifulSoup(pokeRequest.text, 'html.parser')  # Parses the ENTIRE page

    # Let's find the pokemon name...
    pokeName = getPokeName(htmlSouped)

    # Let's find the pokemon description...
    pokeDesc = getPokeDesc(htmlSouped)

    # Times Smashed/Passed + add the user entry
    updDB(number, "passed")
    loadDB(number)
    wouldSmash = smashed
    wouldPass = passed

    # Get the color of the embed
    statusColor = await getColoredEmbed(htmlSouped)

    # Prepare and send the embed with the image
    fileToSend = discord.File("images/" + number + ".png", filename="pokemon.png")

    statusEmbed = discord.Embed(title=f"{pokeName}", description=f"Description: {pokeDesc}",
                                timestamp=ctx.message.created_at, color=statusColor)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldSmash}` users would SMASH this pokemon.", inline=True)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldPass}` users would now pass this pokemon.", inline=True)
    statusEmbed.add_field(name="Passed!", value=f"You wouldn't smash this pokemon. That's good.", inline=False)
    statusEmbed.set_thumbnail(url="attachment://pokemon.png")
    statusEmbed.set_footer(icon_url=botIcon, text="PSoP, version 3.0")
    await deleteEmbed.delete()
    await ctx.send(file=fileToSend, embed=statusEmbed)


# Check command
@client.command(aliases=["stats", "pokemon", "poke"])
@commands.cooldown(1, 15, commands.BucketType.user)
async def check(ctx, number: str):
    # Check for the number
    number, deleteEmbed = await checkPokeNum(number, ctx)
    if number is False:
        return

    number = str(number)
    # Check if the image already exists
    fileCheck = os.path.exists("images/" + number + ".png")
    if fileCheck is False:
        # Do the request (And download the file)
        requestedUrl = str("https://assets.pokemon.com/assets/cms2/img/pokedex/full/" + number + ".png")
        request.urlretrieve(requestedUrl, "images/" + number + ".png")

    # Open page and stuff
    pokeUrl = str("https://www.pokemon.com/us/pokedex/" + number)  # The URL we are using
    pokeRequest = requests.get(pokeUrl, headers={"User-Agent": "Mozilla/5.0"})  # Requests access
    htmlSouped = BeautifulSoup(pokeRequest.text, 'html.parser')  # Parses the ENTIRE page

    # Let's find the Pokemon information...
    pokeName = getPokeName(htmlSouped)
    pokeDesc = getPokeDesc(htmlSouped)
    pokeGender = getPokeGenders(htmlSouped)
    pokeCategory = getPokeCategory(htmlSouped)
    pokeHeight = getPokeHeight(htmlSouped)
    pokeWeight = getPokeWeight(htmlSouped)

    # Times Smashed/Passed
    loadDB(number)
    wouldSmash = smashed
    wouldPass = passed

    # Get the color of the embed
    statusColor = await getColoredEmbed(htmlSouped)

    # Prepare and send the embed with the image
    fileToSend = discord.File("images/" + number + ".png", filename="pokemon.png")

    statusEmbed = discord.Embed(title=f"{pokeName}", description=f"Description: {pokeDesc}",
                                timestamp=ctx.message.created_at, color=statusColor)
    statusEmbed.add_field(name="Gender", value=f"{pokeGender}", inline=True)
    statusEmbed.add_field(name="Height", value=f"{pokeHeight}", inline=True)
    statusEmbed.add_field(name="Weight", value=f"{pokeWeight}", inline=True)
    statusEmbed.add_field(name="Category", value=f"{pokeCategory}", inline=True)
    statusEmbed.add_field(name="Times Smashed", value=f"`{wouldSmash}` users would SMASH.", inline=True)
    statusEmbed.add_field(name="Times Passed", value=f"`{wouldPass}` users would pass.", inline=True)
    statusEmbed.add_field(name="SMASH or PASS?", value=f":punch: = Smash\n:broken_heart: = Pass", inline=True)

    statusEmbed.set_thumbnail(url="attachment://pokemon.png")
    statusEmbed.set_footer(icon_url=botIcon, text="PSoP, version 3.0")
    await deleteEmbed.delete()
    pokeEmbed = await ctx.send(file=fileToSend, embed=statusEmbed)

    # Smash or pass?
    await pokeEmbed.add_reaction("👊")
    await pokeEmbed.add_reaction("💔")

    def reactionCheck(reaction, user):
        return reaction.message.id == pokeEmbed.id and str(reaction.emoji) in ["👊", "💔"] and user == ctx.author

    # Reaction Time
    try:
        reactionUsed, userReacted = await client.wait_for('reaction_add', timeout=20.0, check=reactionCheck)
        # Smash or pass thing
        if reactionUsed.emoji == "👊":
            statusEmbed.add_field(name="👊 You would SMASH that pokemon!",
                                  value="Your choice has been saved into the database.", inline=True)
            updDB(number, "smashed")

        elif reactionUsed.emoji == "💔":
            statusEmbed.add_field(name="💔 You would pass that pokemon.",
                                  value="Your choice has been saved into the database.", inline=True)
            updDB(number, "passed")

    # Timeout, do nothing.
    except asyncio.TimeoutError:
        statusEmbed.add_field(name="Timed out", value=f"Reacting won't do anything anymore.", inline=True)

    # Edit the thing
    await pokeEmbed.edit(embed=statusEmbed)


# Get the Pokémon name
def getPokeName(htmlSpoon):
    pokeName = ""

    # Let's find the Pokémon name!
    spoonedDiv = htmlSpoon.find('div', {"class": "pokedex-pokemon-pagination-title"})  # Finds the specific class

    # Fiddle with rawString
    rawString = str(spoonedDiv.text)  # Gets the text from the specific class
    rawString = rawString.replace("\n", "")  # Removes newlines
    pokeList = rawString.split()  # Splits it into a list
    for num in range(len(pokeList)):  # Iterates in the list
        pokeName = pokeName + pokeList[num]  # Adds the names together, useful if the Pokémon has more than one name.
    return pokeName


# Get the Pokémon description
def getPokeDesc(htmlSpoon):
    # Let's find the pokemon description...
    spoonedDiv = htmlSpoon.find('p', {"class": "version-x"})

    # Fiddle with rawString
    rawString = str(spoonedDiv.text)
    pokeDesc = rawString.lstrip()
    return pokeDesc


# Get the pokemon genders
def getPokeGenders(htmlSpoon):
    # Lets find the pokemon genders...
    pokeGender = "None"
    doMale = False
    doFemale = False
    if htmlSpoon.find_all("i", {'class': {'icon_male_symbol'}}):
        doMale = True
    if htmlSpoon.find_all("i", {'class': {'icon_female_symbol'}}):
        doFemale = True

    # Check for genders
    if doMale is True and doFemale is False:
        pokeGender = ":male_sign: Male"
    elif doFemale is True and doMale is True:
        pokeGender = ":transgender_symbol: Male, Female"
    elif doFemale is True and doMale is False:
        pokeGender = ":female_sign: Female"
    elif doFemale is False and doMale is False:
        pokeGender = ":grey_question: Unknown"
    return pokeGender


# Get the Pokémon category
def getPokeCategory(htmlSpoon):
    # Let's find the pokemon category...
    spoonedDiv = htmlSpoon.find('div', {"class": ["pokemon-ability-info", "match", "color-bg"]})
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


# Get the Pokémon height
def getPokeHeight(htmlSpoon):
    # Let's find the pokemon height...
    spoonedDiv = htmlSpoon.find('div', {"class": {"column-7"}})
    rawString = str(spoonedDiv.text)
    pokeRegex = rawString.replace("\n", "")

    # Fiddle with rawString
    pokeHeight = re.search('Height(.*)Weight', pokeRegex)
    pokeHeight = str(pokeHeight.group(1))
    return pokeHeight


# Get the Pokémon weight
def getPokeWeight(htmlSpoon):
    # Let's find the pokemon weight...
    spoonedDiv = htmlSpoon.find('div', {"class": {"column-7"}})
    rawString = str(spoonedDiv.text)
    pokeRegex = rawString.replace("\n", "")

    # Fiddle with rawString (Again, again, again, again...!)
    pokeWeight = re.search('Weight(.*)Gender', pokeRegex)
    pokeWeight = str(pokeWeight.group(1))
    return pokeWeight


# Check if the Pokémon number is correct
async def checkPokeNum(pokeNum, ctx):
    badNumber = False

    # Starting embed
    processingEmbed = discord.Embed(title=f"Processing Command...", description=f"Please wait a couple of seconds.",
                                    timestamp=ctx.message.created_at, color=settings.defaultColor)
    processingEmbed.set_footer(icon_url=botIcon, text="PSoP, version 3.0")
    processEdit = await ctx.send(embed=processingEmbed)

    # Random number?
    if pokeNum.lower() == "random":
        pokeNum = str(random.randint(1, settings.maxNum))

    # Check if the number is valid (settings.py to update number)
    if pokeNum.isdigit():
        pokeNum = int(pokeNum)
        if pokeNum > settings.maxNum or pokeNum < 1:
            badNumber = True

    # Number length and stuff
    if len(str(pokeNum)) != 3 and badNumber is not True:
        if str(pokeNum).isdigit():
            badNumber = True
            if len(str(pokeNum)) == 1:
                pokeNum = str(pokeNum)
                pokeNum = "00" + pokeNum
                badNumber = False
            elif len(str(pokeNum)) == 2:
                pokeNum = str(pokeNum)
                pokeNum = "0" + pokeNum
                badNumber = False

    # Check if not 404
    if not badNumber:
        pokeNum = str(pokeNum)
        requestedUrl = str("https://www.pokemon.com/us/pokedex/" + pokeNum)
        try:
            _connTest = request.urlopen(requestedUrl)
        except error.HTTPError as e:
            msgTimestamp = str(ctx.message.created_at)
            msgTimestamp = msgTimestamp[11:19]
            print(
                ">> HTTP Error: " + str(e.code) + " || Pokemon: " + pokeNum + " || Timestamp: " + msgTimestamp + " <<")
            badNumber = True

    # Get the number if it's a valid string
    if not badNumber and not pokeNum.isdigit():
        pokeUrl = str("https://www.pokemon.com/us/pokedex/" + pokeNum)  # The URL we are using
        pokeRequest = requests.get(pokeUrl, headers={"User-Agent": "Mozilla/5.0"})  # Requests access
        htmlSouped = BeautifulSoup(pokeRequest.text, 'html.parser')  # Parses the ENTIRE page
        spoonedDiv = htmlSouped.find('div', {"class": "pokedex-pokemon-pagination-title"})  # Finds the specific class
        spoonedDiv = spoonedDiv.find('span', {"class": "pokemon-number"})  # Finds the specific class

        # Fiddle with rawString
        rawString = str(spoonedDiv.text)  # Gets the text from the specific class
        rawString = rawString.replace("\n", "")  # Removes newlines
        pokeNum = str(rawString[1:])

    # If bad then exit
    if badNumber is True:
        errorEmbed = discord.Embed(title=f"Error!",
                                   description=f":x: Sorry, we couldn't find that Pokemon! It might be a server issue or the Pokemon does not exist. You should use '-' if the Pokemon is separated by spaces.",
                                   timestamp=ctx.message.created_at, color=settings.defaultColor)
        errorEmbed.set_footer(icon_url=botIcon, text=f"PSoP, version 3.0")
        await processEdit.edit(embed=errorEmbed)
        return False, processEdit
    else:
        # Pokémon was found!
        goodEmbed = discord.Embed(title=f"Pokemon Found!",
                                  description=f":white_check_mark: Alright, loading the pokemon now!",
                                  timestamp=ctx.message.created_at, color=settings.defaultColor)
        goodEmbed.set_footer(icon_url=botIcon, text="PSoP, version 3.0")
        await processEdit.edit(embed=goodEmbed)

        await asyncio.sleep(1)
        pokeNum = str(pokeNum)
        return pokeNum, processEdit


# Colored embed definition
async def getColoredEmbed(htmlSpoon):  # pokedex-pokemon-attributes
    htmlColor = 0x6338E1
    spoonedDiv = htmlSpoon.find('div', {"class": "dtm-type"})

    # Kill me, cases wouldn't work here for some reason, cover your eyes!
    if spoonedDiv.find_all("li", {"class": "background-color-fire"}):
        htmlColor = 0xE04938
    elif spoonedDiv.find_all("li", {"class": "background-color-water"}) and htmlColor == 0x6338E1:
        htmlColor = 0x327CED
    elif spoonedDiv.find_all("li", {"class": "background-color-grass"}) and htmlColor == 0x6338E1:
        htmlColor = 0x27D855
    elif spoonedDiv.find_all("li", {"class": "background-color-electric"}) and htmlColor == 0x6338E1:
        htmlColor = 0xE2E051
    elif spoonedDiv.find_all("li", {"class": "background-color-bug"}) and htmlColor == 0x6338E1:
        htmlColor = 0x6BAD58
    elif spoonedDiv.find_all("li", {"class": "background-color-flying"}) and htmlColor == 0x6338E1:
        htmlColor = 0xAFCECB
    elif spoonedDiv.find_all("li", {"class": "background-color-rock"}) and htmlColor == 0x6338E1:
        htmlColor = 0xBC8824
    elif spoonedDiv.find_all("li", {"class": "background-color-ice"}) and htmlColor == 0x6338E1:
        htmlColor = 0x6AE5E7
    elif spoonedDiv.find_all("li", {"class": "background-color-poison"}) and htmlColor == 0x6338E1:
        htmlColor = 0xA95CDF
    elif spoonedDiv.find_all("li", {"class": "background-color-psychic"}) and htmlColor == 0x6338E1:
        htmlColor = 0xE036D9
    elif spoonedDiv.find_all("li", {"class": "background-color-normal"}) and htmlColor == 0x6338E1:
        htmlColor = 0x898989
    elif spoonedDiv.find_all("li", {"class": "background-color-dark"}) and htmlColor == 0x6338E1:
        htmlColor = 0x746184
    elif spoonedDiv.find_all("li", {"class": "background-color-dragon"}) and htmlColor == 0x6338E1:
        htmlColor = 0x0C83C6
    elif spoonedDiv.find_all("li", {"class": "background-color-fairy"}) and htmlColor == 0x6338E1:
        htmlColor = 0xB93AA9
    elif spoonedDiv.find_all("li", {"class": "background-color-ghost"}) and htmlColor == 0x6338E1:
        htmlColor = 0x64347F
    elif spoonedDiv.find_all("li", {"class": "background-color-ground"}) and htmlColor == 0x6338E1:
        htmlColor = 0x7F5E34
    elif spoonedDiv.find_all("li", {"class": "background-color-steel"}) and htmlColor == 0x6338E1:
        htmlColor = 0x6B6E80
    elif spoonedDiv.find_all("li", {"class": "background-color-fighting"}) and htmlColor == 0x6338E1:
        htmlColor = 0xDC812C
    return htmlColor


# Loads the smashed and passed Pokémon from the MySQL db.
def loadDB(pokeNum: str):
    global smashed
    global passed
    with db.cursor() as cursor:
        selQuery = f"SELECT * FROM SP WHERE id = %s"
        cursor.execute(selQuery, int(pokeNum))
        sqlDict = cursor.fetchone()
        smashed = sqlDict[1]
        passed = sqlDict[2]


# Saves one of the user's choice into the MySQL db.
def updDB(pokeNum: str, sop: str):
    with db.cursor() as cursor:
        updateQuery = ""
        if sop.lower() == "smashed":
            updateQuery = f"UPDATE SP SET smashed = smashed + 1 WHERE id = %s"
        elif sop.lower() == "passed":
            updateQuery = f"UPDATE SP SET passed = passed + 1 WHERE id = %s"
        cursor.execute(updateQuery, int(pokeNum))


# Starts the bot. Yep, that's it.
client.run(dotenv_values()["BOT_TOKEN"])
