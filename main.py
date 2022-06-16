#Imports
import discord
import settings
import urllib.request, urllib.error
import random
import requests
import asyncio
import json
import os
import re

from discord.ext import commands
from bs4 import BeautifulSoup

#Defining Client
intents=intents=discord.Intents.all()
client = commands.Bot(command_prefix = "sp!", help_command=None, case_insensitive=True, intents = intents)

def __init__(self, client):
	self.client = client

#On ready event
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("sp!help | pokemon.com"))
    global botIcon
    botIcon = "https://cdn.discordapp.com/avatars/942443498915909683/8b1f3a580a07d6045ec8f78fd67003a3.webp?size=80"

    global passed
    global smashed 

    #Prints and databases
    print("====== Bot Stats ======")
    print(" > Logged in as:",str(client.user.name)+"#"+str(client.user.discriminator))
    print(" > Latency: "+str(client.latency)+"ms")
    print("====== Databases ======")

    with open("database/passed.json") as f:
        passed = json.load(f)
        print("     > PPD Loaded")

    with open("database/smashed.json") as f:
        smashed = json.load(f)
        print("     > PSD Loaded")

    print("====== App 404's ======")

#Error handler
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(title="Error! (Member not Found)", description="Sorry, it doesn't seem like that member exists.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Cooldown!", description="Command on cooldown, you'll be able to use this command again in **{:.0f}s**".format(error.retry_after))
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Error! (Missing Argument)", description="Looks like you're missing an argument.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="Error! (Bad Argument)", description="I didn't understand what you said, try again.")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title="Error! (Permissions)", description="Sorry, not enough permissions!")
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
      raise error

#Help Command
@client.command(aliases=["prefix","psop","sop","commands","cmd"])
async def help(ctx):
  embed = discord.Embed(title="PSoP Commands", description="`help`, `check`, `smash`, `pass`, `info`",timestamp=ctx.message.created_at,color=settings.infocolor)
  embed.set_footer(icon_url=botIcon, text="PSoP, ver 1.0")
  await ctx.send(embed=embed)

#Info command
@client.command(aliases=["information","credits"])
async def info(ctx):
  embed = discord.Embed(title="Information", description="This bot was literally made in two days, and I'm not angry about how it looks, it's pretty decent.\nAnyways, all rights go to nintendo blah blah blah.\nThis bot is using requests and soup to access the images from the pokemon pokedex. Made in python by **UnderGame#4540**",timestamp=ctx.message.created_at,color=settings.infocolor)
  embed.add_field(name="Commands:", value=f"All commands accept the Pokemon **ID**, the **name** and '**random**' as arguments. That way you can use them easily.", inline=True)
  embed.set_footer(icon_url=botIcon, text="PSoP, ver 1.0")
  await ctx.send(embed=embed)

#Smash command
@client.command(aliases=["pokeSmash","smashPoke","pokemonSmash","smashPokemon"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def smash(ctx, number: str):
    #Check for the number
    number, deleteEmbed = await checkPokeNum(number, ctx)
    if number == False:
        return

    number = str(number)
    #Check if the image already exists
    fileCheck = os.path.exists("images/poke/"+number+".png")
    if fileCheck == False:
        #Do the request (And download the file)
        requestedUrl = str("https://assets.pokemon.com/assets/cms2/img/pokedex/full/"+number+".png")
        urllib.request.urlretrieve(requestedUrl, "images/poke/"+number+".png")

    #Open page and stuff
    pokeUrl = str("https://www.pokemon.com/us/pokedex/"+number) #The URL we are using
    pokeRequest = requests.get(pokeUrl,headers={"User-Agent":"Mozilla/5.0"}) #Requests access
    htmlSouped = BeautifulSoup(pokeRequest.text,'html.parser') #Parses the ENTIRE page

    #Lets find the pokemon name...
    pokeName = getPokeName(number, htmlSouped)

    #Lets find the pokemon description...
    pokeDesc = getPokeDesc(number, htmlSouped)

    #Times Smashed/Passed + add the user entry
    _load()
    smashed["poke"][number] += 1
    wouldSmash = smashed["poke"][number]
    wouldPass = passed["poke"][number]
    _save()

    #Get the color of the embed
    statusColor = await getColoredEmbed(htmlSouped)

    #Easter eggs
    easterEgg = await checkEaster(number)
    if easterEgg != None:
        pokeDesc = easterEgg

    #Prepare and send the embed with the image
    fileToSend = discord.File("images/poke/"+number+".png", filename="pokemon.png")

    statusEmbed = discord.Embed(title=f"{pokeName}", description=f"Description: {pokeDesc}",timestamp=ctx.message.created_at,color=statusColor)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldSmash}` users would now SMASH this pokemon.", inline=True)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldPass}` users would pass this pokemon.", inline=True)
    statusEmbed.add_field(name="Smashed!", value=f"You would smash this pokemon, heck yeah.", inline=False)
    statusEmbed.set_thumbnail(url="attachment://pokemon.png")
    statusEmbed.set_footer(icon_url=botIcon, text="PSoP, ver 1.0")
    await deleteEmbed.delete()
    await ctx.send(file=fileToSend, embed=statusEmbed)

#Pass command
@client.command(aliases=["pass","passPoke","pokemonPass","passPokemon"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def pokePass(ctx, number: str):
    #Check for the number
    number, deleteEmbed = await checkPokeNum(number, ctx)
    if number == False:
        return

    number = str(number)
    #Check if the image already exists
    fileCheck = os.path.exists("images/poke/"+number+".png")
    if fileCheck == False:
        #Do the request (And download the file)
        requestedUrl = str("https://assets.pokemon.com/assets/cms2/img/pokedex/full/"+number+".png")
        urllib.request.urlretrieve(requestedUrl, "images/poke/"+number+".png")

    #Open page and stuff
    pokeUrl = str("https://www.pokemon.com/us/pokedex/"+number) #The URL we are using
    pokeRequest = requests.get(pokeUrl,headers={"User-Agent":"Mozilla/5.0"}) #Requests access
    htmlSouped = BeautifulSoup(pokeRequest.text,'html.parser') #Parses the ENTIRE page

    #Lets find the pokemon name...
    pokeName = getPokeName(number, htmlSouped)

    #Lets find the pokemon description...
    pokeDesc = getPokeDesc(number, htmlSouped)

    #Times Smashed/Passed + add the user entry
    _load()
    passed["poke"][number] += 1
    wouldSmash = smashed["poke"][number]
    wouldPass = passed["poke"][number]
    _save()

    #Get the color of the embed
    statusColor = await getColoredEmbed(htmlSouped)

    #Easter eggs
    easterEgg = await checkEaster(number)
    if easterEgg != None:
        pokeDesc = easterEgg

    #Prepare and send the embed with the image
    fileToSend = discord.File("images/poke/"+number+".png", filename="pokemon.png")

    statusEmbed = discord.Embed(title=f"{pokeName}", description=f"Description: {pokeDesc}",timestamp=ctx.message.created_at,color=statusColor)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldSmash}` users would SMASH this pokemon.", inline=True)
    statusEmbed.add_field(name="Times Smashed:", value=f"`{wouldPass}` users would now pass this pokemon.", inline=True)
    statusEmbed.add_field(name="Passed!", value=f"You would't smash this pokemon. That's good.", inline=False)
    statusEmbed.set_thumbnail(url="attachment://pokemon.png")
    statusEmbed.set_footer(icon_url=botIcon, text="PSoP, ver 1.0")
    await deleteEmbed.delete()
    await ctx.send(file=fileToSend, embed=statusEmbed)

#Check command
@client.command(aliases=["stats","pokemon","poke"])
@commands.cooldown(1, 15, commands.BucketType.user)
async def check(ctx, number: str):
    #Check for the number
    number, deleteEmbed = await checkPokeNum(number, ctx)
    if number == False:
        return

    number = str(number)
    #Check if the image already exists
    fileCheck = os.path.exists("images/poke/"+number+".png")
    if fileCheck == False:
        #Do the request (And download the file)
        requestedUrl = str("https://assets.pokemon.com/assets/cms2/img/pokedex/full/"+number+".png")
        urllib.request.urlretrieve(requestedUrl, "images/poke/"+number+".png")
        
    #Open page and stuff
    pokeUrl = str("https://www.pokemon.com/us/pokedex/"+number) #The URL we are using
    pokeRequest = requests.get(pokeUrl,headers={"User-Agent":"Mozilla/5.0"}) #Requests access
    htmlSouped = BeautifulSoup(pokeRequest.text,'html.parser') #Parses the ENTIRE page

    #Lets find the pokemon name...
    pokeName = getPokeName(number, htmlSouped)

    #Lets find the pokemon description...
    pokeDesc = getPokeDesc(number, htmlSouped)

    #Lets find the pokemon genders...
    pokeGender = getPokeGenders(number, htmlSouped)

    #Lets find the pokemon category...
    pokeCategory = getPokeCategory(number, htmlSouped)

    #Lets find the pokemon height...
    pokeHeight = getPokeHeight(number, htmlSouped)

    #Lets find the pokemon weight...
    pokeWeight = getPokeWeight(number, htmlSouped)

    #Times Smashed/Passed
    _load()
    wouldSmash = smashed["poke"][number]
    wouldPass = passed["poke"][number]

    #Get the color of the embed
    statusColor = await getColoredEmbed(htmlSouped)

    #Easter eggs
    easterEgg = await checkEaster(number)
    if easterEgg != None:
        pokeDesc = easterEgg

    #Prepare and send the embed with the image
    fileToSend = discord.File("images/poke/"+number+".png", filename="pokemon.png")

    statusEmbed = discord.Embed(title=f"{pokeName}", description=f"Description: {pokeDesc}",timestamp=ctx.message.created_at,color=statusColor)
    statusEmbed.add_field(name="Gender", value=f"{pokeGender}", inline=True)
    statusEmbed.add_field(name="Height", value=f"{pokeHeight}", inline=True)
    statusEmbed.add_field(name="Weight", value=f"{pokeWeight}", inline=True)
    statusEmbed.add_field(name="Category", value=f"{pokeCategory}", inline=True)
    statusEmbed.add_field(name="Times Smashed", value=f"`{wouldSmash}` users would SMASH.", inline=True)
    statusEmbed.add_field(name="Times Passed", value=f"`{wouldPass}` users would pass.", inline=True)
    statusEmbed.add_field(name="SMASH or PASS?", value=f":punch: = Smash\n:broken_heart: = Pass", inline=True)

    statusEmbed.set_thumbnail(url="attachment://pokemon.png")
    statusEmbed.set_footer(icon_url=botIcon, text="PSoP, ver 1.0")
    await deleteEmbed.delete()
    pokeEmbed = await ctx.send(file=fileToSend, embed=statusEmbed)

    #Smash or pass?
    await pokeEmbed.add_reaction("👊")
    await pokeEmbed.add_reaction("💔")
    def reactionCheck(reaction, user):
        return reaction.message.id == pokeEmbed.id and str(reaction.emoji) in ["👊", "💔"] and user == ctx.author

    #Reaction Time
    try:
        reactionUsed, userReacted = await client.wait_for('reaction_add', timeout=20.0, check=reactionCheck)
        #Smash or pass thing
        if reactionUsed.emoji == "👊":
            statusEmbed.add_field(name="👊 You would SMASH that pokemon!", value=f"Your record has been carefully saved into the database.", inline=True)
            smashed["poke"][number] += 1

        elif reactionUsed.emoji == "💔":
            statusEmbed.add_field(name="💔 You would pass that pokemon.", value=f"Your record has been carefully saved into the database.", inline=True)
            passed["poke"][number] += 1

        _save()

    #Timeout, do nothing.
    except asyncio.exceptions.TimeoutError:
        statusEmbed.add_field(name="Timed out", value=f"Reacting won't do anything anymore.", inline=True)

    #Edit the thing
    await pokeEmbed.edit(embed=statusEmbed)

#Get the pokemon name
def getPokeName(pokeNum, htmlSpoon):
    pokeNum = str(pokeNum)
    pokeName = ""

    #Lets find the pokemon name!
    spoonedDiv = htmlSpoon.find('div', {"class" : "pokedex-pokemon-pagination-title"}) #Finds the specific class

    #Fiddle with rawString
    rawString = str(spoonedDiv.text) #Gets the text from the specific class
    rawString = rawString.replace("\n", "") #Removes newlines
    pokeList = rawString.split() #Splits it into a list
    for num in range(len(pokeList)): #Iterates in the list
        pokeName = pokeName+pokeList[num] #Adds the names together, useful if the pokemon has more than one name.
    return pokeName

#Get the pokemon description
def getPokeDesc(pokeNum, htmlSpoon):
    pokeNum = str(pokeNum)

    #Lets find the pokemon description...
    spoonedDiv = htmlSpoon.find('p', {"class" : "version-x"})

    #Fiddle with rawString
    rawString = str(spoonedDiv.text)
    pokeDesc = rawString.lstrip()
    return pokeDesc

#Get the pokemon genders
def getPokeGenders(pokeNum, htmlSpoon):
    pokeNum = str(pokeNum)

    #Lets find the pokemon genders...
    pokeGender = "None"
    doMale = False
    doFemale = False
    if htmlSpoon.find_all("i", {'class': {'icon_male_symbol'}}):
        doMale = True
    if htmlSpoon.find_all("i", {'class': {'icon_female_symbol'}}):
        doFemale = True

    #Check for genders
    if doMale == True and doFemale == False:
        pokeGender = ":male_sign: Male"
    elif doFemale == True and doMale == True:
        pokeGender = ":transgender_symbol: Male, Female"
    elif doFemale == True and doMale == False:
        pokeGender = ":female_sign: Female"
    elif doFemale == False and doMale == False:
        pokeGender = ":grey_question: Unknown"
    return pokeGender

#Get the pokemon category
def getPokeCategory(pokeNum, htmlSpoon):
    pokeNum = str(pokeNum)

    #Lets find the pokemon category...
    spoonedDiv = htmlSpoon.find('div', {"class" : ["pokemon-ability-info", "match", "color-bg"]})
    rawString = str(spoonedDiv.text)
    pokeRegex = rawString.replace("\n", "")
    abilityCount = int(pokeRegex.lower().count('abilities'))

    #Fiddle with rawString
    if abilityCount > 1:
        pokeCategory = ":warning: Cannot load."
    else:
        pokeCategory = re.search('Category(.*)Abilities', pokeRegex)
        pokeCategory = str(pokeCategory.group(1))
    return pokeCategory

#Get the pokemon height
def getPokeHeight(pokeNum, htmlSpoon):
    pokeNum = str(pokeNum)

    #Lets find the pokemon height...
    spoonedDiv = htmlSpoon.find('div', {"class" : {"column-7"}})
    rawString = str(spoonedDiv.text)
    pokeRegex = rawString.replace("\n", "")

    #Fiddle with rawString
    pokeHeight = re.search('Height(.*)Weight', pokeRegex)
    pokeHeight = str(pokeHeight.group(1))
    return pokeHeight

#Get the pokemon weight
def getPokeWeight(pokeNum, htmlSpoon):
    pokeNum = str(pokeNum)

    #Lets find the pokemon weight...
    spoonedDiv = htmlSpoon.find('div', {"class" : {"column-7"}})
    rawString = str(spoonedDiv.text)
    pokeRegex = rawString.replace("\n", "")

    #Fiddle with rawString (again again again again!)
    pokeWeight = re.search('Weight(.*)Gender', pokeRegex)
    pokeWeight = str(pokeWeight.group(1))
    return pokeWeight

#Check if the pokemon number is correct
async def checkPokeNum(pokeNum, ctx):
    badNumber = False

    #Starting embed
    processingEmbed = discord.Embed(title=f"Processing Command...", description=f"Please wait a couple of seconds.",timestamp=ctx.message.created_at,color=settings.infocolor)
    processingEmbed.set_footer(icon_url=botIcon, text="PSoP, ver 1.0")
    processEdit = await ctx.send(embed=processingEmbed)

    #Random number?
    if pokeNum.lower() == "random":
        pokeNum = str(random.randint(1,898))

    #Check if the number is valid (for pokemons 898 max)
    if pokeNum.isdigit() == True:
        pokeNum = int(pokeNum)
        if pokeNum > 898 or pokeNum < 1:
            badNumber = True

    #Number length and stuff
    if len(str(pokeNum)) != 3 and badNumber != True:
        if str(pokeNum).isdigit() == True:
            badNumber = True
            if len(str(pokeNum)) == 1:
                pokeNum = str(pokeNum)
                pokeNum = "00"+pokeNum
                badNumber = False
            elif len(str(pokeNum)) == 2:
                pokeNum = str(pokeNum)
                pokeNum = "0"+pokeNum
                badNumber = False

    #Check if not 404
    if badNumber == False:
        pokeNum = str(pokeNum)
        requestedUrl = str("https://www.pokemon.com/us/pokedex/"+pokeNum)
        try:
            connTest = urllib.request.urlopen(requestedUrl)
        except urllib.error.HTTPError as e:
            msgTimestamp = str(ctx.message.created_at)
            msgTimestamp = msgTimestamp[11:19]
            print(">> HTTP Error: "+str(e.code)+" || Pokemon: "+pokeNum+" || Timestamp: "+msgTimestamp+" <<")
            badNumber = True

    #Get the number if its a valid string
    if badNumber == False and pokeNum.isdigit() == False:
        pokeUrl = str("https://www.pokemon.com/us/pokedex/"+pokeNum) #The URL we are using
        pokeRequest = requests.get(pokeUrl,headers={"User-Agent":"Mozilla/5.0"}) #Requests access
        htmlSouped = BeautifulSoup(pokeRequest.text,'html.parser') #Parses the ENTIRE page
        spoonedDiv = htmlSouped.find('div', {"class" : "pokedex-pokemon-pagination-title"}) #Finds the specific class
        spoonedDiv = spoonedDiv.find('span', {"class" : "pokemon-number"}) #Finds the specific class

        #Fiddle with rawString
        rawString = str(spoonedDiv.text) #Gets the text from the specific class
        rawString = rawString.replace("\n", "") #Removes newlines
        pokeNum = str(rawString[1:])
  
    #If bad then exit
    if badNumber == True:
        errorEmbed = discord.Embed(title=f"Error!", description=f":x: Sorry, we could't find that Pokemon! It might be a server issue or the Pokemon does not exist. You should use '-' if the Pokemon is separated by spaces.",timestamp=ctx.message.created_at,color=settings.infocolor)
        errorEmbed.set_footer(icon_url=botIcon, text="PSoP, ver 1.0")
        await processEdit.edit(embed=errorEmbed)
        return False, processEdit
    else:
        #Pokemon was found!
        goodEmbed = discord.Embed(title=f"Pokemon Found!", description=f":white_check_mark: Alright, loading the pokemon now!",timestamp=ctx.message.created_at,color=settings.infocolor)
        goodEmbed.set_footer(icon_url=botIcon, text="PSoP, ver 1.0")
        await processEdit.edit(embed=goodEmbed)
        
        await asyncio.sleep(1)
        pokeNum = str(pokeNum)
        return pokeNum, processEdit

#Colored embed definition
async def getColoredEmbed(htmlSpoon): #pokedex-pokemon-attributes
    htmlColor = 0x6338E1 
    spoonedDiv = htmlSpoon.find('div', {"class" : "dtm-type"})
    #Kill me
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

#Easter eggs time!
async def checkEaster(pokeNum):
    easterG = None
    if pokeNum == "134": #Vaporeon
        easterG = "Hey guys, did you know that in terms of male human and female Pokémon breeding, Vaporeon is the most compatible Pokémon for humans? Not only are they in the field e-"
    elif pokeNum == "132": #Ditto
        easterG = "Sorry, no description for you. This one's overrated."
    elif pokeNum == "758": #Salazzle
        easterG = "Kinky."
    elif pokeNum == "447": #Riolu
        easterG = "What is wrong with you?"
    elif pokeNum == "448": #Lucario
        easterG = "Now this is something different i'd say."
    elif pokeNum == "133": #Eevee
        easterG = "Eevee my beloved, one of the best mons by far."
    elif pokeNum == "872": #Snom
        easterG = "This is the most adorable pokemon in the entire pokedex, you cannot change my mind."
    elif pokeNum == "815": #Cinderace
        easterG = "*Music starts*, HAHAHA. Ronaldinho socceeeeeeeeer!"
    elif pokeNum == "428": #Lopunny
        easterG = "Does this technically make me a furry? - Markiplier 2022"
    elif pokeNum == "706": #Goodra
        easterG = "No comments, dunno why people like Goodra that much."
    elif pokeNum == "655": #Delphox 
        easterG = "Now that's hot. Haha, ha, haha.. Get it?"
    elif pokeNum == "015": #Beedrill 
        easterG = "That's some masochist material over here, ain't I right?"
    elif pokeNum == "069": #Bellsprout 
        easterG = "Nice."
    elif pokeNum == "071": #Victreebel 
        easterG = "That, uhhh, that doesn't look safe at all."
    elif pokeNum == "121": #Starmie 
        easterG = "[3 AM CHALLENGE] Me when dot is inside a discord bot (real) **police called** 4k FREE DOWNLOAD."
    elif pokeNum == "197" or pokeNum == "196": #Espeon+Umbreon 
        easterG = "The best non-canon ship of the community, love them both :heart:"
    elif pokeNum == "250": #Ho-Oh 
        easterG = "Ho-Oh, you're approaching me? Well. Then come as close as you'd like!"
    elif pokeNum == "282": #Gardevoir 
        easterG = "Too good to be true, don't really know why everyone likes it."
    elif pokeNum == "329": #Vibrava 
        easterG = "Underrated pokemon, give it some love!"
    elif pokeNum == "463": #Lickilicky 
        easterG = "WHY THE FU- NINTENDO."
    elif pokeNum == "545": #Scolipede 
        easterG = "This will kill you, don't even think about it."
    elif pokeNum == "563": #Cofagrigus 
        easterG = "The 'Coffin Pokemon'. You can already tell what do I mean."
    elif pokeNum == "596": #Galvantula 
        easterG = "THE GIANT ENEMY SPIDER *music*"
    elif pokeNum == "778": #Mimikyu 
        easterG = "Actually, I won't judge you on this one. Looks interesting."
    elif pokeNum == "807": #Zeraora 
        easterG = "A classic, of course."
    elif pokeNum == "865": #Sirfetch'd 
        easterG = "You pet the doggo, it's neck grew bigger."
    elif pokeNum == "700": #Sylveon 
        easterG = "Best eeveelution, I'm 100% Based."
    return easterG

#Load database
def _load():
    global passed
    global smashed
    with open("database/passed.json") as f:
        passed = json.load(f)
    with open("database/smashed.json") as f:
        smashed = json.load(f)

#Save database
def _save():
    with open("database/passed.json", 'w') as f:
        json.dump(passed, f, indent=4)
    with open("database/smashed.json", 'w') as f:
        json.dump(smashed, f, indent=4)

#Starts the bot. Yep, that's it.
client.run("YOUR BOT TOKEN")