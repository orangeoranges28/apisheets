from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

import discord
from discord import ui
from discord.ext import tasks, commands

from datetime import datetime, timedelta
import asyncio

import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=".", intents=intents)

SERVICE_ACCOUNT_FILE, SCOPES = 'keys.json', ['https://www.googleapis.com/auth/spreadsheets']

creds = None

creds, sheetid, ab = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES), '1f9sEMKppr9GIh6u6q6MqoVr9Rzpph7jbMaGPsx3bgYA', ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()



@client.command()
async def quit(ctx):
    await ctx.reply("Shutting down bot")

@client.event
async def on_ready(): 
    channel = client.get_channel(1012193036035432501)
    print("Online - "+(datetime.now()-timedelta(hours=8)).strftime('%H:%M') + " - " +(datetime.today()-timedelta(hours=8)).strftime('%m/%d/%y'))
    await updateHoursDisc()
    time_check.start(channel)
    daily_brief.start(channel)
    topicUpdate.start(channel)

@client.command()
async def clear(ctx, amount = 4):
 
  amount+=1
  await ctx.channel.purge(limit = amount)


async def updateHoursDisc():
    channel = client.get_channel(1012193036035432501)
    result = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!I7").execute().get('values', [])
    if len(await channel.pins()) < 3:
        for i in await channel.pins():
            if "Total Hours: " in i.content and i.author == client.user:
                i = await i.edit(content="__**Total Hours: "+str(result).strip("hours taught[]''")+"**__") 
                break
    else:
        [await i.unpin() for i in await channel.pins() if "Total Hours: " in i.content and i.author == client.user]
        i = await channel.send("__**Total Hours: "+str(result).strip("hours taught[]''")+"**__") 

        await i.pin()

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="as "+str(result).strip("hours taught[]''")+" hours pile up"))
    if int(str(result).strip("hours taught[]''")) % 100 == 0:
        await channel.send("Milestone reached! "+str(result).strip("hours taught[]''")+" total hours taught 🥳")

    

@client.command(name="commands")
async def help(ctx):
    ctx.reply("**Commands**.addHours [first] [second] [amount (optional)] - add hours to a teacher by an amount (optional)\n.gmail - get link to 425kidschess@gmail.com \n.log - get link to 425 Kids Chess log")

@client.command(name="unpinHours")
async def unpin(channel):
    [await i.unpin() for i in await channel.pins() if "Total Hours: " in i.content and i.author == client.user]


@client.command(name="log")
async def getLog(ctx):
    await ctx.reply("https://docs.google.com/spreadsheets/d/1f9sEMKppr9GIh6u6q6MqoVr9Rzpph7jbMaGPsx3bgYA")

@client.command(name="gmail", aliases = ["email"])
async def getGmail(ctx):
    await ctx.reply("https://mail.google.com/mail/u/?authuser=425kidschess@gmail.com")


@client.command(name="whobest")
async def whobest(ctx):
    await ctx.reply("brandon luo is the best - made this bot")

@client.command(name="brandon")
async def whobest(ctx):
    await ctx.reply("me when brandon: ♥♥😍♥♥")

@client.command(name="addHours")
async def addHours(name, second = "", amount=1):
    if second != "":
        person = name+" "+second
    
    person = name
    try:

        rawAvalues = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A:A").execute().get('values')

        Avalues = sum(rawAvalues, [])

        for _ in range(amount):

            cellUpdate = "USE THIS SHEET!"+"E"+str([idx for idx in range(len(Avalues)) if person in Avalues[idx]][0]+2)

            newCell = sheet.values().get(spreadsheetId=sheetid, range=cellUpdate).execute().get('values', [])

            if newCell[0][0] == 0:
                newCell[0][0] = 1

            else:
                newCell[0][0] = int(newCell[0][0])+1

            sheet.values().update(spreadsheetId=sheetid, range=cellUpdate, valueInputOption="USER_ENTERED", body ={"values":newCell}).execute()

            #Hour Log:
            hourLogRow = str(rawAvalues.index([person])+1)

            rowV = len(sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A"+hourLogRow+":ZZZ"+hourLogRow).execute().get('values', [])[0])
            
            if rowV/26 < 1:
                cellUpdate = "USE THIS SHEET!"+ab[rowV]+hourLogRow

            else:
                cellUpdate = "USE THIS SHEET!"+ab[int(rowV/26-1)]+ab[rowV%26]+hourLogRow

            sheet.values().update(spreadsheetId=sheetid, range=cellUpdate, valueInputOption="USER_ENTERED", body={"values":[[(datetime.today()-timedelta(hours=8)).strftime('%#m/%#d/%#y')]]}).execute()

            await updateHoursDisc()

    except HttpError as err:
        print(err)
        channel = client.get_channel(1012193036035432501)
        await channel.send("add hours failed "+person+str((datetime.today()-timedelta(hours=8)).strftime('%#m/%#d/%#y')))

    

@tasks.loop(minutes=1)
async def time_check(channel):

    Avalues = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A:A").execute().get('values', [])

    now = (datetime.now()-timedelta(hours=8)+timedelta(minutes=5)).strftime('%#H:%M')

    print(datetime.strptime(now, '%H:%M').strftime('%#I:%M')) 

    values = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A1:K999").execute().get('values', [])


    if "Interviewee" in str(Avalues):
        for i in range(1, Avalues.index(["Monday"])):
            next = values[i]
            if next == []:
                continue
            elif "Interviewee" in next[0]:
                time = next[2].split()
                if time[0] == (datetime.today()-timedelta(hours=8)).strftime('%#m/%#d/%#y') and time[1]+" "+time[2] == datetime.strptime(now, '%H:%M').strftime('%#I:%M %p'):
                    embed = discord.Embed()
                    embed.title = "INTERVIEW ALERT - "+time[1]
                    if "https://" not in next[1]:
                        embed.description = "Interview happening now at " + time[1]+" with "+next[0].split("Interviewee: ")[1]+"\nLink: https://"+next[1]
                    else:
                        embed.description = "Interview happening now at " + time[1]+" with "+next[0].split("Interviewee: ")[1]+"\nLink: "+next[1]
                    embed.color = discord.Color.green()
                    
                    await channel.send("<@&1020489761036697703>", embed=embed)
                    break


    for i in range(Avalues.index([(datetime.today()-timedelta(hours=8)).strftime('%A')]), len(values)):
        next = values[i]       
        print(next)
        if len(next) == 1:
            return
        
        if next == []:
            continue
        elif ((datetime.today()-timedelta(hours=8)+timedelta(days=1))).strftime('%A') in next[0] or "Hour Log:" in next[0]:
            break

        elif (datetime.strptime(now, '%H:%M')).strftime('%#I:%M') in next[2][:5] and (datetime.strptime(now, '%H:%M')).strftime('%p') in next[2] and "Ongoing" in next[1]:
            print(next)
            total = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A1:Z999").execute().get('values', [])
            sheet.values().update(spreadsheetId=sheetid, range="safety [DO NOT DELETE]!A1", valueInputOption="USER_ENTERED", body={"values":total}).execute()

            embed = discord.Embed()
            embed.title = "LESSON ALERT - "+next[2].split("-")[0]

            if next[7] == "":
                student = next[8]
            else:
                student = next[7]

            if "https://" not in next[3]:
                embed.description = "Lesson happening now at " + next[2]+" with "+next[4]+" teaching "+student+"\nLink: https://"+next[3]
            else:
                embed.description = "Lesson happening now at " + next[2]+" with "+next[4]+" teaching "+student+"\nLink: "+next[3]
            embed.color = discord.Color.blue()

            if next[4] == "":
                await channel.send("<@&1012195802468323328> - auto unavailable (teacher error)", embed=embed)

            else:                
                button1 = ui.Button(label="all", style=discord.ButtonStyle.green, custom_id=next[4]+"$everyone")
                button2 = ui.Button(label="none", style=discord.ButtonStyle.red, custom_id="$none")
                button3 = ui.Button(label="sub", style=discord.ButtonStyle.blurple, custom_id="sub")
                button4 = ui.Button(label="special", style=discord.ButtonStyle.gray, custom_id="special")
                
                async def button_callback1(interaction):
                    await interaction.response.edit_message(content="<@&1012195802468323328> logged hour for "+ interaction.data.get("custom_id").split("$")[0], view=None)
                    await addHours(interaction.data.get("custom_id").split("$")[0])
                    
                
                async def button_callback2(interaction):
                    await interaction.response.edit_message(content="<@&1012195802468323328> logged no attendance", view=None)

                async def button_callback3(interaction):
                    await interaction.response.send_message(content="who subbed")

                    try:  
                        response = await client.wait_for("message", timeout=480, check=lambda message: "sub" in message.content)
                    
                    except asyncio.TimeoutError:
                        await interaction.message.edit(content="<@&1012195802468323328> voided - no response", view=None)
                        return

                    answer = response.content.title()[4:]

                    if answer == "Stop" or answer == "End" or answer == ".end" or answer == ".stop":
                        await response.reply("Finished")
                    
                    await addHours(answer)
                    await response.reply("nice - hours added for "+answer)
                    await interaction.message.edit(content="<@&1012195802468323328> logged sub hour for "+answer, view=None)

                async def button_callback4(interaction):
                    await interaction.response.defer()
                    await interaction.message.edit(content="<@&1012195802468323328> nothing logged", view=None)
                
                button1.callback = button_callback1
                button2.callback = button_callback2
                button3.callback = button_callback3
                button4.callback = button_callback4

                view = discord.ui.View(timeout=1800)
                view.add_item(button1)
                view.add_item(button2)
                view.add_item(button3)
                view.add_item(button4)

                await channel.send("<@&1012195802468323328>", embed=embed, view=view)         
            
        


@tasks.loop(minutes=10)
async def topicUpdate(channel):
    Avalues = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A:A").execute().get('values', [])

    deltas = []
    time = ""

    values = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A1:K999").execute().get('values', [])

    for i in range(Avalues.index([(datetime.today()-timedelta(hours=8)).strftime('%A')]), len(values)):
        next = values[i]

        if len(next) == 1:
            next = values[Avalues.index([(datetime.today()+timedelta(hours=18)).strftime('%A')])]
            time += "tomorrow "
            print(next)

        else:
            if next == []:
                continue        
            
            elif ((datetime.today()-timedelta(hours=8)+timedelta(days=1))).strftime('%A') in next[0] or "Hour Log:" in next[0]:
                break

            elif "Ongoing" in next[1]:
                hour = int(next[2].split("-")[0].split(":")[0])

                if (hour == 12):
                    hour = 0
                if ('PM' in next[2]):
                    hour += 12

                delta = datetime.strptime(str(hour)+":" + str(next[2].split("-")[0].split(":")[1]), '%H:%M') - datetime.strptime(datetime.strftime(datetime.now(), "%H:%M"), '%H:%M')

                if delta.days == 0:
                    deltas.append((delta, next))


        
                deltas.sort()

                next = deltas[0][1]

    time += next[2].split("-")[0]+" "+next[2].split()[1]

    if next[7] == "":
        student = next[8]
    else:
        student = next[7]

    if "https://" not in next[3]:
        await channel.edit(topic="next meeting: "+ time+" - " + next[4] +" teaching "+student+", link: https://"+next[3])
    else:
        await channel.edit(topic="next meeting: "+ time+" - " + next[4] +" teaching "+student+", link: "+next[3])
        
    

@tasks.loop(hours=1)
async def daily_brief(channel):
    Avalues = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A:A").execute().get('values', [])
    values = sheet.values().get(spreadsheetId=sheetid, range="USE THIS SHEET!A1:K999").execute().get('values', [])

    embed = discord.Embed()
    embed.title = "Lessons for today: "+(datetime.today()-timedelta(hours=8)).strftime('%#m/%#d/%#y')
    embed.description = ""    

    now = (datetime.now()-timedelta(hours=8)+timedelta(minutes=5)).strftime('%#H:%M')

    for i in range(Avalues.index([(datetime.today()-timedelta(hours=8)).strftime('%A')]), len(values)):
        next = values[i]
        if len(next) == 1:
            return

        if next == []:
            continue
        elif ((datetime.today()-timedelta(hours=8)+timedelta(days=1))).strftime('%A') in next[0] or "Hour Log:" in next[0]:
            break
        elif "Ongoing" not in next[1]:
            continue
        
        elif "Interviewee" in next[0]:
            time = next[2].split()
            if time[0] == (datetime.today()-timedelta(hours=8)).strftime('%#m/%#d/%#y') and time[1]+" "+time[2] == datetime.strptime(now, '%H:%M').strftime('%#I:%M %p'):
                embed = discord.Embed()
                embed.title = "INTERVIEW ALERT - "+time[1]
                if "https://" not in next[1]:
                    embed.description += "**" + time[1]+"** - "+next[0].split("Interviewee")[1]+"\nLink: https://"+next[1]
                else:
                    embed.description = "**" + time[1]+"** - "+next[0].split("Interviewee")[1]+"\nLink: "+next[1]
                
                await channel.send("<@&1012195802468323328>", embed=embed)

        if i > 0:
            embed.description+="\n\n"

        if "PM" in next[2]:
            startTime = next[2].split("-")[0].strip()+" PM"
        elif "AM" in next[2]:
            startTime = next[2].split("-")[0].strip()+" AM"

        if next[7] == "":
                student = next[8]
        else:
            student = next[7]
        
        if "https://" not in next[3]:
            embed.description += "**" + startTime+"** - "+next[4]+" teaching "+student+"\nLink: https://"+next[3]
        else:
            embed.description += "**" + startTime+"** - "+next[4]+" teaching "+student+"\nLink: "+next[3]
        embed.color = discord.Color.purple()

    if (datetime.now()-timedelta(hours=8)).strftime('%H %p') == "07 AM":
        [await i.unpin() for i in await channel.pins() if "<@&1014306387783843860>" in i.content and i.author == client.user]
        newDaily = await channel.send(content="<@&1014306387783843860>", embed=embed)
        await newDaily.pin()

    else:
        for i in await channel.pins():
            if "<@&1014306387783843860>" in i.content and i.author == client.user:
                await i.edit(content="<@&1014306387783843860>", embed=embed)
                break
        

        

    

client.run(str(os.getenv("key")))