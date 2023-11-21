import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os

import asyncio
# Define intents
'''
intents = discord.Intents.default()
#intents.message_content = True
intents.members = True
intents.presences = True
'''
intents = discord.Intents.default()
intents.messages = True  # Correct attribute for message content
intents.members = True
intents.presences = True


#bot = commands.Bot(command_prefix='!', intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)


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

    elif before.self_video != after.self_video:

        if after.channel is not None:
 
            if member.name not in user_activity: 
                async with lock:
                    user_activity[member.name] = {'start_time': datetime.now(), 'total_time': timedelta(),'studying':True, 'Video':True, 'Screen':False}
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
                    user_activity[member.name] = {'start_time': datetime.now(), 'total_time': timedelta(),'studying':True, 'Video':False, 'Screen':True}
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



            


@tasks.loop(minutes=1/2)
async def print_activity():
    for user_id, activity in user_activity.items():
        if user_activity[user_id]['studying'] == True:
            user_activity[user_id]['total_time'] += datetime.now() - user_activity[user_id]['start_time']
            user_activity[user_id]['start_time'] = datetime.now()
        print(f"User {user_id} has been active for {activity['total_time']}")

    # Save user activity to a text file
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"user_activity_{date_str}.txt"
    with open(filename, 'w') as file:
        print(user_activity)
        for user_id, activity in user_activity.items():
            user = user_id#bot.get_user(user_id)
            print(user)
            if user!= None:
                print("wrote in the file")
                file.write(f"{user}: {activity['total_time']}\n")
                #file.write(f"{user.name}: {activity['total_time']:.2f} minutes\n")

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
    for user_id, activity in user_activity.items():
        user = user_id#bot.get_user(user_id)
        print(user)
        if user!= None:
            print("wrote in the file")
            say = str(f"{user}: {activity['total_time']}\n")
            await ctx.send(say)


@bot.command(name='state')
async def state(ctx):
    user_id = ctx.author.name
    if user_id in user_activity:
        state = str(user_activity[user_id]['studying'])
        await ctx.send(f"your studying state is "+ state)
    else:
        await ctx.send("You have no recorded activity or state.")


@bot.command(name='timerr')
async def reminderr(ctx, minutes: int):
    """Set a reminder for the specified number of minutes."""
    await ctx.send(f"Reminder set for {minutes} minutes.")
    await asyncio.sleep(minutes * 60)
    await ctx.send(f"{ctx.author.mention}, time's up! Your reminder has arrived.")

@bot.command(name='old_data')
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
    for i in listt:
        await ctx.send(i)


@bot.command(name='pika')
async def commandhelp(ctx):
    await ctx.send("Commands are:- ")
    await ctx.send("* **!mystats** -- This shows your universal stats (or stats after the event started)")

    await ctx.send("* **!todaystats** -- Everyone's today's stats")         

    await ctx.send("* **!allstats** -- Everyone's Universal stats (or stats after the event started)")   
    await ctx.send("* **!state** -- Tells your state as recorded by the bot. True = studying. if you are studying with cam/screen share. but it shows false, contact @estrizal")              
    await ctx.send("* **!timerr** -- Reminds you after the mentioned time.")
    await ctx.send("* **!old_data** -- gives you data of mentioned no. of days. like put 4 for stats of today + past 3 days.")
    await ctx.send("* **!pika** -- this command you just used")
    await ctx.send("* One more command is there. it starts the event by clearing all the stats of everyone present in the server. but only admins can use it.")

              

        

@bot.command(name='AdminEventStart')
async def clear(ctx):
    global user_activity
    user_activity = {}
    await ctx.send("Cleared all the scores for you. Though, todaystats will still have uncleared stats")



# Run the bot
bot.run('MTE3NjM1ODg5MTU2NzcxMDI2OA.GCPpcp.FdM2PWyhKMU9f_m2gk2danTyMTAPZHbCVxvq3s') #I accidently revealed my token here.. now it's automatically resetted. AHHHHHHHHH gotta re run bot.py in my VM again..

print("bot is up and running")
