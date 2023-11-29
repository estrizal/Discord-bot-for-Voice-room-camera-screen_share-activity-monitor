import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os
import json
import asyncio
import ast
from discord import Member
import math
import pytz
# Define intents

intents = discord.Intents.default()
intents.messages = True  # Correct attribute for message content
intents.members = True
intents.presences = True


#bot = commands.Bot(command_prefix='!', intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

Warn = 10
# Dictionary to store user activity



user_activity = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')


lock = asyncio.Lock()
@bot.event
async def on_voice_state_update(member, before, after):
    print(f"{member.name} changed voice state: {before.channel} -> {after.channel}")
    if before.channel is not None and after.channel is None: #someone left the server.
        if member.name in user_activity:
            async with lock:
                user_activity[member.name]['studying'] = False
                user_activity[member.name]['Video'] = False
                user_activity[member.name]['Screen'] = False
                user_activity[member.name]['joined'] = False

    elif before.self_video != after.self_video:
        if after.channel is not None:
            if member.name not in user_activity: 
                async with lock:
                    user_activity[member.name] = {'start_time': datetime.now(), 'total_time': timedelta(),'studying':True, 'Video':True, 'Screen':False, 'joined':True,'warn_time': 0.0,'member':member.id}
            else:

                if user_activity[member.name]['studying'] == True and user_activity[member.name]['Screen'] == False: #kuch video mai change hua hai. and.. agr padh rhe the aur screen false hai. to false set karo
                    async with lock:
                        user_activity[member.name]['studying'] = False
                        user_activity[member.name]['Video'] = False

                elif user_activity[member.name]['studying'] == True and user_activity[member.name]['Screen'] == True: #Kuch video mai change hua and agr padh rhe the and screen on hai. to true hi rahne do. 

                    async with lock:
                        user_activity[member.name]['Video'] = not user_activity[member.name]['Video']
                        user_activity[member.name]['studying'] = True
                        user_activity[member.name]['start_time'] = datetime.now()

                elif user_activity[member.name]['studying'] == False and user_activity[member.name]['Screen'] == False: #kuch video mai change hua hai agr padh nahi rhe the and screen bhi off thi to True kr de
                    async with lock:
                        user_activity[member.name]['Video'] = True
                        user_activity[member.name]['studying'] = True
                        user_activity[member.name]['start_time'] = datetime.now()



    elif before.self_stream != after.self_stream:

        if after.channel is not None:

            if member.name not in user_activity:
                async with lock:
                    user_activity[member.name] = {'start_time': datetime.now(), 'total_time': timedelta(),'studying':True, 'Video':False, 'Screen':True, 'joined':True,'warn_time':0.0, 'member':member.id}
            else:
                if user_activity[member.name]['studying'] == True and user_activity[member.name]['Video'] == False: #kuch video mai change hua hai. and.. agr padh rhe the aur screen false hai. to false set karo
                    async with lock:
                        user_activity[member.name]['studying'] = False
                        user_activity[member.name]['Screen'] = False


                elif user_activity[member.name]['studying'] == True and user_activity[member.name]['Video'] == True: #Kuch video mai change hua and agr padh rhe the and screen on hai. to true hi rahne do. 
                    async with lock:
                        user_activity[member.name]['Screen'] = not user_activity[member.name]['Screen']
                        user_activity[member.name]['studying'] = True
                        user_activity[member.name]['start_time'] = datetime.now()

                elif user_activity[member.name]['studying'] == False and user_activity[member.name]['Video'] == False: #kuch video mai change hua hai agr padh nahi rhe the and screen bhi off thi to True kr de
                    async with lock:
                        user_activity[member.name]['Screen'] = True
                        user_activity[member.name]['studying'] = True
                        user_activity[member.name]['start_time'] = datetime.now()

    elif after.channel is not None: #Someone Entered the server. 
        if member.name in user_activity:
            user_activity[member.name]['joined'] = True

        else:
            user_activity[member.name] = {'start_time': datetime.now(), 'total_time': timedelta(),'studying':False, 'Video':False, 'Screen':False, 'joined':True,'warn_time': 0.0,'member':member.id}






@tasks.loop(minutes=1/2)



async def print_activity():
    try:
        for user_id, activity in user_activity.items():
            if user_activity[user_id]['studying'] == True:
                user_activity[user_id]['total_time'] += datetime.now() - user_activity[user_id]['start_time']
                user_activity[user_id]['start_time'] = datetime.now() 
                user_activity[user_id]['warn_time'] = 0.0

            else:
               try:
                if user_activity[user_id]['joined'] == True:
                    user_activity[user_id]['warn_time'] += 0.5
                    if user_activity[user_id]['warn_time'] == float(Warn):
                        userID = user_activity[user_id]['member']
                        userr = await bot.fetch_user(userID)
                        #userr = user_activity[user_id]['member']
                        await userr.send(f"Hey It seems like you haven't turned on your camera or screen share in the last {Warn} minutes. Please contact @estrizal(aditya) if your screen/cam is on, but you still got this message.")
               
               except Exception as SSt:
                try:
                    userr = await bot.fetch_user(756014504004812910)
                    await userr.send("Boss I got this error"+ str(SSt + "user ID is " + str(user_activity[user_id]['member'])))
                except:
                    print("god sabe this child")

            print(f"User {user_id} has been active for {activity['total_time']}")

        # Save user activity to a text file
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"user_activity_{date_str}.txt"
        print("\n \n today's date is ", date_str, "\n \n ")

        try:
            with open(filename, 'r') as f:
                f.read()


            with open(filename, 'w') as file:
                print(user_activity)
                for user_id, activity in user_activity.items():
                    user = user_id#bot.get_user(user_id)
                    print(user)
                    if user!= None:
                        print("wrote in the file")
                        file.write(f"{user}: {activity['total_time']}\n")
                        #file.write(f"{user.name}: {activity['total_time']:.2f} minutes\n")
            
        except:
            with open(filename, 'w') as file:
                for user_id, activity in user_activity.items():
                    user = user_id
                    if user!= None:
                        print("wrote in the NEWWW file")
                        user_activity[user_id]['total_time'] = timedelta()
                        file.write(f"{user}: {user_activity[user_id]['total_time']}\n")

    except Exception as SSt:
        try:
            userr = await bot.fetch_user(756014504004812910)
            await userr.send("Boss I got this error"+ str(SSt))

        except:
            print("god sabe me somehowww")



        

#loopp = asyncio.get_event_loop()
print_activity.start()

@bot.command(name='mystats')
async def my_stats(ctx):
    print("Command received!")
    user_id = ctx.author.name
    if user_id in user_activity:
        total_time = user_activity[user_id]['total_time']
        await ctx.send(f"You have been active for {total_time}.")
    else:
        await ctx.send("You have no recorded activity.")

@bot.command(name='todaystats')
async def today_stats(ctx):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"user_activity_{date_str}.txt"
    with open(filename, 'r') as file:
        r = file.read()
    await ctx.send(r)

@bot.command(name='allstats')
async def all_stats(ctx):
    say = ''
    for user_id, activity in user_activity.items():
        user = user_id#bot.get_user(user_id)
        print(user)
        if user!= None:
            print("wrote in the file")
            say = say + str(f"{user}: {activity['total_time']}\n")
        
    print(say)
    await ctx.send(say)


@bot.command(name='state')
async def state(ctx):
    user_id = ctx.author.name
    if user_id in user_activity:
        state = str(user_activity[user_id]['studying'])
        await ctx.send(f"your studying state is "+ state)
    else:
        await ctx.send("You have no recorded activity or state.")


@bot.command(name='allstates')
async def allstates(ctx):
    s = ''
    for user_id, activity in user_activity.items():
        state = str(user_activity[user_id]['studying'])
        s = s + str(user_id + " : "+ state)+"\n"
    
    await ctx.send(s)




@bot.command(name='timerr')
async def reminderr(ctx, minutes: int):
    """Set a reminder for the specified number of minutes."""
    await ctx.send(f"Reminder set for {minutes} minutes.")
    await asyncio.sleep(minutes * 60)
    await ctx.send(f"{ctx.author.mention}, time's up! Your reminder has arrived.")

@bot.command(name='old_stats')
async def olddata(ctx, dayss: int):
    listt=[]
    def read_activity_file(file_path):
        """Read and parse the content of a user activity file."""
        user_times = {}
        with open(file_path, 'r') as file:
            for line in file:
                username, time_str = line.strip().split(': ')
                user_times[username] = user_times.get(username, timedelta()) + parse_time(time_str)
        return user_times

    def parse_time(time_str):
        """Parse the time string in the format HH:MM:SS.microseconds."""
        # Split the time string into hours, minutes, and seconds
        time_components = time_str.split(':')

        # Extract the hours and minutes
        hours = int(time_components[0])
        minutes = int(time_components[1])
        
        # Extract the seconds and ignore values after the decimal point
        seconds = int(time_components[2].split('.')[0])

        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    def main():
        # Get today's date
        today = datetime.now().date()

        # Initialize variables to store total times
        total_times = {}

        # Loop through the past 30 days (adjust as needed)
        for i in range(dayss):
            # Calculate the date for the current iteration
            current_date = today - timedelta(days=i)

            # Generate the file name based on the current date
            file_name = f"user_activity_{current_date.strftime('%Y-%m-%d')}.txt"

            # Check if the file exists
            if os.path.exists(file_name):
                # Read and parse the activity file
                user_times = read_activity_file(file_name)

                # Update the total times
                for username, time_delta in user_times.items():
                    total_times[username] = total_times.get(username, timedelta()) + time_delta
            else:
                # Break the loop if the file doesn't exist
                break

        # Print the total times for each user
        for username, total_time in total_times.items():
            listt.append(f"{username}: {total_time}")

    main()
    say = ""
    for i in listt:
        say = say + i + "\n"
    await ctx.send(say)


@bot.command(name='backup')
async def backitup(ctx):
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime, timedelta)):
                return str(obj)
            '''
            elif isinstance(obj, Member):
                return {
                    'id': obj.id,
                    'name': obj.name,
                    'discriminator': obj.discriminator,
                    'bot': obj.bot,
                    'nick': obj.nick
                }
            '''
            return super().default(obj)
    global user_activity
    actual_activity = user_activity
    s = ''
    for user_id, activity in actual_activity.items():
        actual_activity[user_id]['studying'] = False
        actual_activity[user_id]['Video'] = False
        actual_activity[user_id]['Screen'] = False

    with open('data.json', 'w') as json_file:
        json.dump(actual_activity, json_file, cls=CustomEncoder)
        print("wrote the whole activity.")
        await ctx.send("wrote the whole activity.")



@bot.command(name='date')
async def backitup(ctx):
    date_str = datetime.now().strftime("%Y-%m-%d")
    await ctx.send(date_str)


@bot.command(name='load')
async def load_it(ctx):
    global user_activity

    def custom_decoder(obj):
        if 'start_time' in obj:
            obj['start_time'] = datetime.strptime(obj['start_time'], '%Y-%m-%d %H:%M:%S.%f')
        if 'total_time' in obj:
            # Assuming the format of 'total_time' is 'H:M:S'
            #hours, minutes, seconds = map(int, obj['total_time'].split(':'))
            totall = obj['total_time'].split(':')
            hours = int(totall[0])
            minutes = int(totall[1])
            seconds = totall[2]
            seconds = int(math.floor(float(seconds)))
            #print("\n \n \n"+stseconds+"\n \n \n")
            obj['total_time'] = timedelta(hours=hours, minutes=minutes, seconds=int(math.floor(seconds)))
        return obj

    try:
        with open('data.json', 'r') as json_file:
            jason_Data= json_file.read()
            loaded_dict = json.loads(jason_Data, object_hook=custom_decoder)

        user_activity = loaded_dict#json.loads(test_string)
        await ctx.send("loaded the whole activity.")
    
    except Exception as P:
        print(P)
        await ctx.send("Couldn't load activity because"+str(P))






@bot.command(name='changeactivity')
async def olddata(ctx, *args):
    global user_activity
    try:
        print("username doneeeeeeeeeeeeeeeeeee")
        user_name, thing, bhalue = args[:3]
        print("user info extractedddddddddddd")
        keyy = thing.split(":")
        print('split doneeeeeeeeeeee')
        valuee = bhalue.split(":")
        print('split 2 doneeeeeeeee')
        my_dict = dict(zip(keyy, valuee))
        print('zippingggggg')
        print(my_dict)

        for k,v in my_dict.items():
                print("loop runnin",k)
                if k == 'Video' and v == 't':
                    user_activity[user_name]['Video'] = True

                if k == 'Video' and v == 'f':
                    user_activity[user_name]['Video'] = False

                if k == 'Screen' and v == 't':
                    user_activity[user_name]['Screen'] = True

                if k == 'Screen' and v == 'f':
                    user_activity[user_name]['Screen'] = False

                if k == 'studying' and v == 't':
                    user_activity[user_name]['studying'] = True

                if k == 'studying' and v == 'f':
                    user_activity[user_name]['studying'] = False

                if k == 'total_time':
                    user_activity[user_name]['total_time'] += timedelta(minutes=int(v))

        await ctx.send("Updated")

    except Exception as SmallU:
        try:
            await ctx.send(str(SmallU))
        except:
            await ctx.send("an error has occured")
            




    

@bot.command(name='allactivity')
async def activity(ctx):
    global user_activity
    await ctx.send(str(activity))

@bot.command(name='pika')
async def commandhelp(ctx):
    await ctx.send("Commands are:- ")
    a = "* **!mystats** -- This shows your universal stats (or stats after the event started)\n"

    b = "* **!todaystats** -- Everyone's today's stats\n"       

    c = "* **!allstats** -- Everyone's Universal stats (or stats after the event started)\n"
    d = "* **!state** -- Tells your state as recorded by the bot. True = studying. if you are studying with cam/screen share. but it shows false, contact @estrizal\n"            
    e="* **!timerr** -- Reminds you after the mentioned time.\n"
    f="* **!old_stats** -- gives you data of mentioned no. of days. like put 4 for stats of today + past 3 days.\n"
    g = "* **!pika** -- this command you just used\n"
    h = "* **allstates** -- Tells studying state of everyone. True = studying.\n"
    i = "* One more command is there. it starts the event by clearing all the stats of everyone present in the server. but only admins can use it."
    await ctx.send(a + b + c + d + e + f + g + h + i )

 

              

        

@bot.command(name='AdminEventStart')
async def clear(ctx):
    global user_activity
    user_activity = {}
    await ctx.send("Cleared all the scores for you. Though, todaystats will still have uncleared stats")



# Run the bot
bot.run('YOUR TOKEN')
print("bot is up and running")
