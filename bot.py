import discord
import urllib.parse
from discord.ext import commands
import asyncio
import requests as rq
desc = "test"
contrv = ["nothingyet5435435435435"]
bot = commands.Bot(command_prefix='...', description=desc)
chars = {"a":"🇦🅰🔼🖇️","b":"🇧🅱","c":"🇨©☪️","d":"🇩↩🌮","e":"🇪📧3⃣","f":"🇫🎏","g":"🇬6⃣","h":"🇭♓","i":"🇮ℹ📍🎚","j":"🇯🗾🌶️☂️🏑","k":"🇰🎋💃","l":"🇱💪👢1⃣🎚","m":"🇲Ⓜ♏〽️♍","n":"🇳♑📈","o":"🇴🅾⭕💿⚙","p":"🇵🅿🚩","q":"🇶🎯","r":"🇷♌®","s":"🇸💲💰⚡","t":"🇹✝️🌴⛏","u":"🇺⛎♉","v":"🇻♈🔽✔️☑️","w":"🇼〰🌵🐍","x":"🇽✖️","y":"🇾🌱✌️","z":"🇿💤"," ":"⚪▫️◼️🔲🔳","!":"❗❕","?":"❓❔","+":"➕","-":"➖"}
nums = ["0⃣","⏺️🔘🔄🔵","1⃣","🥇☝️","2⃣","🥈","3⃣","🥉","4⃣","","5⃣","","6⃣","","7⃣","🎰","8⃣","🎱","9⃣ ",""]
long_chars = {"100":"💯","abc":"🔤","10":"🔟","!?":"⁉️","!!":"‼️","tm":"™","end":"🔚","back":"🔙","on":"🔛","top":"🔝","soon":"🔜","free":"🆓","new":"🆕","cool":"🆒","up":"🆙","ok":"🆗","ng":"🆖","wc":"🚾","atm":"🏧","18":"🔞","sos":"🆘","cl":"🆑","ab":"🆎","vs":"🆚","id":"🆔","31":"📆📅"}

banned_ids = ['']

##TELLS ME I'VE LOGGED IN
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(game=discord.Game(name=":help"))
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
        if str(message.author.id) in banned_ids: await bot.send_message(message.channel,message.author.mention+"  is banned from (ab)using this bot.");return ""
        hp = discord.Embed(title="Bot Help", description="**View challenges:** `:lxcx` (`l2x3`)\n**Add reactions:** `:react x abc` (`:react 1 hi`)\n**LMGTFY link:** `:lmgtfy (optional:@user) how to do xyz`  |  (`:lmgtfy @Georgee1991 how to loop in python`)\n**Haveibeenpwned Search:** `:haveibeenpwned user@email.com`  |  (`:haveibeenpwned george@gmail.com`)\n**Haveibeenpwned password search:** `:hasitbeenpwned password`  |  (`:hasitbeenpwed password1234`)", colour=0xf44256)
        hp.set_author(name="George's Python :) Bot", icon_url="https://game.joincyberdiscovery.com/assets/images/asset-game-agent-8.png?version=2.0.8")
        await bot.send_message(message.channel,embed=hp)


##WHOPINGED/debato
@bot.listen()
async def on_message(message):
    text = message.content
    if ("@everyone" in text.lower()) or ("@here" in text.lower()):
        if str(message.author.id) in banned_ids: return ""
        reaction_list = ["🙁","🇼","🇭","🇴","🔵","🇵","🇮","🇳","🇬","🇪","🇩"]
        for x in reaction_list: await bot.add_reaction(message,x)
    elif "dabato" in text.lower():
        if str(message.author.id) in banned_ids: return ""
        await bot.add_reaction(message,"🤔")

##LMGTFY
@bot.listen()
async def on_message(message):
    text = message.content
    if text.startswith(':lmgtfy'):
        if str(message.author.id) in banned_ids: await bot.send_message(message.channel,message.author.mention+"  is banned from (ab)using this bot.");return ""
        delete = False
        explainer = False
        if "-delete" in text.lower():
            text = text.replace("-delete","")
            delete = True
        if "-ie" in text.lower():
            text = text.replace("-ie","")
            explainer = True
        messagetext = text[9:].rstrip()
        if message.mentions:
            for x in message.mentions: text = text.replace(str(x.mention),"")
            url = "https://lmgtfy.com/?q="+urllib.parse.quote_plus(messagetext)
            if explainer == True: url += "&iie=1"
            url = "  |  " +rq.get("http://tinyurl.com/api-create.php?url="+url).text
            await bot.send_message(message.channel,message.mentions[0].mention+url)
        else:
            url = "https://lmgtfy.com/?q="+urllib.parse.quote_plus(messagetext)
            if explainer == True: url += "&iie=1"
            url = rq.get("http://tinyurl.com/api-create.php?url="+url).text
            await bot.send_message(message.channel,url)
        if delete == True:
            await bot.delete_message(message)

##REACT STUFF V2:
###ADD CUSTOM ReACTIONS
@bot.listen()
async def on_message(message):
    text = (message.content).lower()
    if text.startswith(":react"):
        if str(message.author.id) in banned_ids: await bot.send_message(message.channel,message.author.mention+"  is banned from (ab)using this bot.");return ""
        print(str(message.author)+" reacted with: "+text.replace(":react ",""))

###For recording logs
        try:
            channel = bot.get_channel(str(390209703726022659))
            await bot.send_message(channel, (str(message.author).replace("@","")) +"reacted with: "+(text.replace(":react ",""))[1:])
        except:
            pass
###

        chan = message.channel; auth = str(message.author.mention)
        text = text.split(" ")
#marked out becos collm is a collosal bellend <3
        try: await bot.delete_message(message)
        except: pass
        try: num = int(text[1])-1;actual_text = ' '.join(text[2:])
        except: num = 0;actual_text = ' '.join(text[1:])
        mgs = []
        async for x in bot.logs_from(chan,limit = num+1): mgs.append(x)
        foundmessage = mgs[num]
        if len(foundmessage.reactions) > 19:
            msg = await bot.send_message(chan,auth+"  |  Maximum reactions added (**20**)!")
            await asyncio.sleep(4)
            await bot.delete_message(msg)
        for long in long_chars:
            if (long in actual_text): actual_text = actual_text.replace(long,long_chars[long],1)
        used = ""
        for char in actual_text:
            if char in chars:
                try:
                    actual_text = actual_text.replace(char,chars[char][used.count(char)],1)
                except IndexError:
                    pass
                used += char
        used = ""
        for char in actual_text:
            try:
                if (char not in used) and (char in "0123456789"): await bot.add_reaction(foundmessage,nums[int(char)*2]);used += char
                elif (char in used) and (char in "0123456789"): await bot.add_reaction(foundmessage,nums[(int(char)*2)+1][used.count(char)-1]);used += char
                else: await bot.add_reaction(foundmessage,char)
            except discord.errors.HTTPException as ex:
                if "Unknown Emoji" in str(ex):
                    continue
                elif "Maximum number of reactions reached" in str(ex):
                    msg = await bot.send_message(chan,auth+"  |  Maximum reactions added (**20**)!")
                    await asyncio.sleep(7)
                    await bot.delete_message(msg)
                    break
                else: print(ex)

#Headquarters
@bot.listen()
async def on_message(message):
    if (message.content.startswith(':l')) and ("lmgtfy" not in str(message.content)):
        if str(message.author.id) in banned_ids: await bot.send_message(message.channel,message.author.mention+"  is banned from (ab)using this bot.");return ""
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
    #    print ("Starting message printing")
        em = discord.Embed(title=("Level " + str(inp[0] + 1) + " Challenge " + str(inp[1] + 1) + " - " + text.splitlines()[0]), description=text, colour=0x4262f4)
    #    print ("Setting author")
        em.set_author(name="Cyber Discovery", icon_url="https://pbs.twimg.com/profile_images/921313066515615745/fLEl2Gfa_400x400.jpg")
    #    print ("Sending now")
        await bot.send_message(message.channel, embed=em)

#haveibeenpwned
@bot.listen()
async def on_message(message):
    url = "https://haveibeenpwned.com/api/v2/breachedaccount/"
    if message.content.startswith(":haveibeenpwned"):
        if str(message.author.id) in banned_ids: await bot.send_message(message.channel,message.author.mention+"  is banned from (ab)using this bot.");return ""
        text = (message.content).replace(":haveibeenpwned ","")
        try:
            r = (rq.get(url+text)).json()
        except:
            await bot.send_message(message.channel,str(message.author.mention)+"  |  This account has never been breached!")
            return ""
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
            pwu = discord.Embed(title="Pwned Passwords", description=str(message.author.mention)+"  |  This password has been uncovered "+text+" times.",colour=0x5DBCD2)
            pwu.set_author(name="have i been pwned?",icon_url="https://upload.wikimedia.org/wikipedia/commons/2/23/Have_I_Been_Pwned_logo.png")
            await bot.send_message(message.channel,embed=pwu)
        except:
            pwc = discord.Embed(title="Pwned Passwords", description=str(message.author.mention)+"  |  This password has never been uncovered", colour=0x5DBCD2)
            pwc.set_author(name="have i been pwned?",icon_url="https://upload.wikimedia.org/wikipedia/commons/2/23/Have_I_Been_Pwned_logo.png")
            await bot.send_message(message.channel,embed=pwc)


#joke tings
@bot.listen()
async def on_message(message):
    text = (message.content).lower()
    if "13" in text:
#        ogtext = text
        text = str((message.clean_content))
#        if message.raw_mentions:
#            for x in message.raw_mentions: text = text.replace(str(x),"")
#        if message.raw_channel_mentions:
#            for x in message.raw_channel_mentions: text = text.replace(str(x),"")
        if "13" not in text: return ""
        try: text = text.split("13")[1]
        except: text = text.replace("13","",1)
        if ("1" in text  or "one" in text.lower()) and ("11" not in text) and ("12" not in text) and str(message.author) != "cyberdiscovery-bot#8010":
            msg = await bot.send_message(message.channel,str(message.author.mention)+"  |  13.1 is a no-hint zone. 🚫 ⛔ 🙅")
            print(str(message.author)+" said the cursed phrase:"+text)
            if "keep" not in text:
                await asyncio.sleep(4)
                await bot.delete_message(msg)
    elif "thirteen" in text.lower():
        text = str((message.clean_content))
#        if message.raw_mentions:
#            for x in message.raw_mentions: text = text.replace(str(x),"")
#        if message.raw_channel_mentions:
#            for x in message.raw_channel_mentions: text = text.replace(str(x),"")
        text = (text.lower()).split("thirteen")[1]
        if "one" in text.lower() or "1" in text.lower() and ("11" not in text) and ("12" not in text):
            msg = await bot.send_message(message.channel,str(message.author.mention)+"  |  13.1 is a no-hint zone. 🚫 ⛔ 🙅")
            print(str(message.author)+" said the cursed phrase:"+text.replace(".1",""))
            if "keep" not in text:
                await asyncio.sleep(4)
                await bot.delete_message(msg)
    text = text.split(" ")
    if len(text) == 2 and ((text[0]).lower() == "git"):
        if not any(x in text[1].lower() for x in ['blame','branch','status','add','commit','rm','push','checkout','merge','stash','pull','remote','log','diff']):
            takenmessage = str(text[1]).replace("`","")
            gitmsg = """```ruby
git: '"""+takenmessage+"""' is not a git command. Did you mean 'git push'?```"""
            await bot.send_message(message.channel,gitmsg)

#Helping with common questions
@bot.listen()
async def on_message(message):
    text = (message.content).lower()
    if all(x in text for x in ['when','game']) and any(i in text for i in ['did']) and any(n in text for n in ['end','finish','close']):
        await bot.send_message(message.channel,str(message.author.mention)+"  |  Cyberstart Game ended on the 29th May.")
    elif all(x in text for x in ['when','essentials']) and any(i in text for i in ['?','does','will']) and any(n in text for n in ['end','finish','close']):
        await bot.send_message(message.channel,str(message.author.mention)+"  |  Cyberstart Essentials ends on the 18th June.")
    elif all(x in text for x in ['how','elite','get','to']):
        await bot.send_message(message.channel,str(message.author.mention)+"  |  **Quote from the @CyberDiscUK Twitter: **Selection for CyberStart Elite will be based on a combination of Game and Essentials results.")



bot.run('APIKEY')
