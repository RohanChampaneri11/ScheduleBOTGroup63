import os
import re
import sys
import csv
from pathlib import Path
from types import TracebackType

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".../")))
from src.functionality.export_file import load_key, encrypt_file, decrypt_file

def delete_type(rows, msg_content):
    """
    Function:
        delete_type
    Description:
        A existing event type is deleted from the user's calendar file   
    Input:
        rows: lsit of lines in calendar
        msg_content: event type to be deleted
    Output:
        - A existing event type is deleted from the user's calendar file 
    """
    flag=0
    line_number = 0
    new_row=[]
    for line in rows:
        if str(line[0]) == msg_content :
            flag=1
        else:
            new_row.append(line)
            line_number+=1
    temp=[new_row, flag, line_number]
    return temp

def print_type(calendar_lines):
    """
    Function:
        print_type
    Description:
        Sends the lsit of all event type in csv file
    Input:
        calendar_lines - object for csv.reader for user's calendar file
    Output:
        -  Sends the lsit of all event types as list and string
    """
    list_types=''
    rows = []
    #print (calendar_lines)
    for line in calendar_lines:

        if len(line) > 0:
            rows.append(line)
            list_types= list_types + "\nEvent Type: " + str(line[0]) + " prefered time range from " + str(line[1]) +" to " +str(line[2])
    temp1= [rows, str(list_types)]
    return temp1


async def delete_event_type(ctx, client):
    """
    Function:
        delete_event_type
    Description:
        Walks a user through deleting the existing event types in the calender file
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - A existing event type is deleted from the user's calendar file 
        - A message sent to the context saying an event type was successfully deleted
    """
    line_number = 0
    channel = await ctx.author.create_dm()
    print(ctx.author.id)
    key = load_key(str(ctx.author.id))
    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    filename =str(ctx.author.id) + "event_types"
    try:

        # Checks if the calendar csv file exists
        if not os.path.exists(os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv"):
            await channel.send("You have not created any events type yet!!")
        else:
            # Decrypt the file
            decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(ctx.author.id) + "event_types" + ".csv")
            dec = True
            # Opens the current user's csv calendar file
            with open(
                os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv", "r"
            ) as calendar_lines:
                calendar_lines = csv.reader(calendar_lines, delimiter=",")
                fields = next(calendar_lines)  # The column headers will always be the first line of the csv file
                
                new_row=[]
                #printing the list of event type
                temp1=print_type(calendar_lines)
                rows = temp1[0]
                list_types=temp1[1]

                if list_types=='':
                    await channel.send("You have not created any events type yet!!")
                else:
                    await channel.send("List of your available events types are:" + list_types)

                    await channel.send("Please enter the event type to be deleted")
                    # Waits for user input
                    event_msg = await client.wait_for("message", check=check)
                    # Strips message to just the text the user entered
                    msg_content = str(event_msg.content)

                    # Searching and deleting the event type
                    temp= delete_type(rows, msg_content)
                    new_row=temp[0]
                    flag= temp[1]
                    line_number = temp[2]
                
                    if flag==0:
                        await channel.send("Event type does not exist")
                    if flag==1:
                        await channel.send("Event type " + msg_content +" has been deleted.")

                 # Open current user's calendar file for writing
                with open(
                    os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv", "w", newline=""
                ) as calendar_file:
                    # Write to column headers and array of rows back to the calendar file
                    csvwriter = csv.writer(calendar_file)
               # print (str(fields))
               # print (str(new_row))
                    csvwriter.writerow(fields)
                    if line_number > 1:
                        csvwriter.writerows(new_row)
                    elif line_number == 1:
                        csvwriter.writerow(new_row[0])
            encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(ctx.author.id) + "event_types" + ".csv")
    except Exception as e:
        # Outputs an error message if the event could not be created
        print(e)

        if dec:
            encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(ctx.author.id) + "event_types" + ".csv")
        await channel.send(
            "There was an error deleting your event."
        )
