import discord
import urllib.parse
from discord.ext import commands
import asyncio
import requests as rq
desc = "test"
contrv = ["not very nice"]
bot = commands.Bot(command_prefix='...', description=desc)

##TELLS ME I'VE LOGGED IN
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


##CONTROVERSIAL FILTER
@bot.listen()
async def on_message(message):
    text = message.content
    if (any(x in text.lower() for x in contrv)) and (str(message.author) != "cyberdiscovery-bot#8010"):
        msg = await bot.send_message(message.channel, message.author.mention+"  |  *Please refrian from discussing controversial topics in this discord, **as mentioned in rule 2**.\nThis includes discussion of race, religion, politics, gender and sexuality.*")
        await asyncio.sleep(5)
        await bot.delete_message(msg)
    elif "@someone" in text.lower():
        await bot.delete_message(message)


##Help
@bot.listen()
async def on_message(message):
    if message.content.startswith(":help"):
        hp = "View challenges: `:lxcx` (`l2x3`)\nAdd reactions: `:react x abc` (`:react 1 hi`)\nLMGTFY link: `:lmgtfy (optional:@user) how to do xyz`  |  (`:lmgtfy @Georgee1991 how to loop in python`)\nHaveibeenpwned Search: `:haveibeenpwned user@email.com`  |  (`:haveibeenpwned george@gmail.com`)\nHaveibeenpwned password search: `:hasitbeenpwned password`  |  (`:hasitbeenpwed password1234`)"
        await bot.send_message(message.channel,hp)


##WHOPINGED/debato
@bot.listen()
async def on_message(message):
    text = message.content
    if ("@everyone" in text.lower()) or ("@here" in text.lower()):
        reaction_list = ["🙁","🇼","🇭","🇴","🔵","🇵","🇮","🇳","🇬","🇪","🇩"]
        for x in reaction_list: await bot.add_reaction(message,x)
    elif "dabato" in text.lower():
        await bot.add_reaction(message,"🤔")

##LMGTFY
@bot.listen()
async def on_message(message):
    text = message.content
    delete = False
    if "-delete" in text.lower():
        text = text.replace("-delete","")
        delete = True
    if text.startswith(':lmgtfy'):
        if message.mentions:
            for x in message.mentions: text = text.replace(str(x.mention),"")
            url = "https://lmgtfy.com/?q="+urllib.parse.quote_plus(text[9:])
            url = "  |  " +rq.get("http://tinyurl.com/api-create.php?url="+url).text
            await bot.send_message(message.channel,message.mentions[0].mention+url)
        else:
            url = "https://lmgtfy.com/?q="+urllib.parse.quote_plus(text[8:])
            url = rq.get("http://tinyurl.com/api-create.php?url="+url).text
            await bot.send_message(message.channel,url)
        if delete == True:
            await bot.delete_message(message)

###ADD CUSTOM ReACTIONS
@bot.listen()
async def on_message(message):
    text = (message.content).lower()
    if message.content.startswith(':react') and any(x in text for x in contrv) == False:
        text = text.split(" ")
        try:
            num = int(text[1])
        except ValueError:
            await bot.send_message(message.channel,str(message.author.mention)+"  |  Correct syntax: `:react <number of messages up to react to> <text>` (e.g. `:react 1 abc`).")
            return ""
        mgs = []
        async for x in bot.logs_from(message.channel,limit = num+1):
            mgs.append(x)
        foundmessage = mgs[num]
        actual_text = ' '.join(text[2:])
        regional_chars = "🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿 ◽".split(" ")
        repeat_chars = "🅰 🅱 © ↩ 8⃣ 🇫 🇬 ♓ ℹ 🗾 🇰 🇱 Ⓜ ♑ 🅾 🅿 🇶 ® 💲 ✝️ ⛎ ♈ 🇼 ✖️ 🇾 💤 ⚪".split(" ")
        numbers = "0⃣ 1⃣ 2⃣ 3⃣ 4⃣ 5⃣ 6⃣ 7⃣ 8⃣ 9⃣ 🔟".split(" ")
        empt = ""
        for char in actual_text:
            if char == " ": char = "{"
            if char in "0123456789":
                try:
                    await bot.add_reaction(foundmessage,numbers[int(char)])
                except discord.errors.Forbidden:
                    msg = await bot.send_message(message.channel,str(message.author.mention)+"  |  Too many reactions!")
                    await asyncio.sleep(7)
                    await bot.delete_message(msg)
                    break
                continue
            try: newchar = regional_chars[ord(char)-97]
            except: newchar=regional_chars[26]
            if newchar in empt:
                try: newchar = repeat_chars[ord(char)-97]
                except: newchar = repeat_chars[26]
            empt += newchar
            try: await bot.add_reaction(foundmessage,newchar)
            except discord.errors.Forbidden:
                msg = await bot.send_message(message.channel,str(message.author.mention)+"  |  Too many reactions!")
                await asyncio.sleep(20)
                await bot.delete_message(msg)
                break
            except discord.errors.HTTPException: pass
        await bot.delete_message(message)

#Headquarters
@bot.listen()
async def on_message(message):
    if (message.content.startswith(':l')) and ("lmgtfy" not in str(message.content)):
        text = ((message.content).split(" "))[0]
        text = (text).lower().replace(":","")
        try:
            inp = text.split("c")
            for count,x in enumerate(inp): inp[count] = int(x.replace("l",""))-1
        except ValueError:
            await bot.send_message(message.channel,str(message.author.mention)+"  |  Correct syntax: `:lxcx` where x is the level/challenge number (e.g. `:l5c6`).")
            return ""
        if (inp[0]+1 not in range(1,14)) or (inp[1]+1 not in range(1,13)):
            msg = await bot.send_message(message.channel,str(message.author.mention)+"  |  Challenge not in range!")
            await asyncio.sleep(5)
            await bot.delete_message(msg)
            return ""
        with open('headquarters.txt','r') as f:
            text = (f.read()).split(";;;;;;")
        text = text[inp[0]]
        text = text.split(":::")
        try:
            text = text[inp[1]]
        except:
            await bot.send_message(message.channel,str(message.author.mention)+"  |  ")
            return ""
        print ("Starting message printing")
        em = discord.Embed(title=("Level " + str(inp[0] + 1) + " Challenge " + str(inp[1] + 1) + " - " + text.splitlines()[0]), description=text, colour=0x4262f4)
        print ("Setting author")
        em.set_author(name="Cyber Discovery", icon_url="https://pbs.twimg.com/profile_images/921313066515615745/fLEl2Gfa_400x400.jpg")
        print ("Sending now")
        await bot.send_message(message.channel, embed=em)

@bot.listen()
async def on_message(message):
    url = "https://haveibeenpwned.com/api/v2/breachedaccount/"
    if message.content.startswith(":haveibeenpwned"):
        text = (message.content).replace(":haveibeenpwned ","")
        r = (rq.get(url+text)).json()
        writing = str(message.author.mention)+"  |  Info from `https://haveibeenpwned.com/`. Showing up to **5** breaches (Total: "+str(len(r))+")"
        await bot.send_message(message.channel,writing)
        for i in r[:5]:
            writing ="```Title: "+i['Title']+"\nName: "+i['Name']+"\nBreach date: "+i['BreachDate']+"\nPwnCount"+str(i['PwnCount'])+"\nDescription: "+(i['Description']).replace("<a href=\"","").replace("\" target=\"_blank\" rel=\"noopener\">","").replace("</a>","")
            writing += "\nLost data: "+'/'.join(i['DataClasses'])+"\nCurrently active: "+str(i['IsActive'])+"```"
            await bot.send_message(message.channel,writing)
    elif message.content.startswith(":hasitbeenpwned"):
        url = "https://api.pwnedpasswords.com/pwnedpassword/"
        text = (message.content).replace(":hasitbeenpwned ","")
        try:
            text = str((rq.get(url+text)).json())
            await bot.send_message(message.channel,str(message.author.mention)+"  |  This password has been uncovered "+text+" times.")
        except:
            await bot.send_message(message.channel,str(message.author.mention)+"  |  This password has never been uncovered :)")



bot.run('')
