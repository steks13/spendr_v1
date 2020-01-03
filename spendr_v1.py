import gspread
from oauth2client.service_account import ServiceAccountCredentials
import discord
from discord.ext import commands
import os
import datetime
import asyncio


print(discord.__version__)

# static variables
sheet_date_index = 1
sheet_day_name_index = 2
daily_spending_sheet_spending_index = 3
daily_spending_sheet_balance_index = 4
daily_spending_sheet_weekly_balance_index = 5
daily_spending_sheet_last_weekly_balance_row_index = 11

total_balance_row_index = 2
total_balance_column_index = 8

weekly_income_row_index = 2
weekly_income_col_index = 8
weekend_counter_row_index = 2
weekend_counter_col_index = 10

MONDAY = 0
SATURDAY = 5
SUNDAY = 6

weekly_savings_column_index = 6
savings_multiplier_column_index = 12

weekday_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

discord_bot_private_key = os.environ["discord_priv_key"]
secret_dict = {
     "type": os.environ["type"],
     "project_id": os.environ["project_id"],
     "private_key_id": os.environ["private_key_id"],
     "private_key": os.environ["private_key"],
     "client_email": os.environ["client_email"],
     "client_id": os.environ["client_id"],
     "auth_uri": os.environ["auth_uri"],
     "token_uri": os.environ["token_uri"],
     "auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
     "client_x509_cert_url": os.environ["client_x509_cert_url"]
}

# set up google spreadsheet
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_dict, scope)

client_gspread = gspread.authorize(creds)
daily_spending_sheet = client_gspread.open("daily_spending").sheet1
dailly_spending_to_update = client_gspread.open("daily_spending")


# ______________________________________________________________________________________________________________________
#                                                   Spreadsheets
# ______________________________________________________________________________________________________________________
def refresh_google_tokens():
    if creds.access_token_expired:
        print("tokens expired")
        print("Refreshing credentials ...")
        client_gspread.login()
        print("Refreshed credentials.")


def get_all_raw_data():
    return daily_spending_sheet.get_all_values()


def get_nb_rows(all_raw_data):
    # return the number of filled in rows in integer type
    return len(all_raw_data)


def fill_in_daily_row(row, date, spending_amount, balance):
    date_string = get_edited_date_string_with_date(date)
    weekday_string = weekday_list[get_weekday_with_date(date)]
    row_to_fill_in_list = [[date_string, weekday_string, spending_amount, balance]]
    print(row_to_fill_in_list)
    dailly_spending_to_update.values_update('Blad1!A{}'.format(row),
                                            params={'valueInputOption': 'RAW'},
                                            body={'values': row_to_fill_in_list}
                                            )


def get_date_from_spreadsheet_row(all_raw_data, row):
    date_string = all_raw_data[row - 1][sheet_date_index - 1]
    return get_date_with_edited_string(date_string)


def fill_in_initial_weekly_balance(row):
    daily_spending_sheet.update_cell(row, daily_spending_sheet_weekly_balance_index, 0)


def get_last_row_date(all_raw_data):
    nb_rows = get_nb_rows(all_raw_data)
    if nb_rows > 1:
        return get_date_from_spreadsheet_row(all_raw_data, nb_rows)
    else:
        return None


def convert_gspread_string_to_float(string):
    print("input string: ", string)
    new_string = string.replace(',', '.')
    print("new string: ", new_string)
    return float(new_string)


# #####################################
# ##########    Dates   ###############
# #####################################
def get_todays_date():
    # return todays date in date type
    return datetime.date.today()


def split_date(date):
    # input type datetime.date
    # output a list of integers [yyyy, mm, dd]
    date_string = str(date)
    year = date_string[0:4]
    month = date_string[5:7]
    day = date_string[8:10]
    return [int(year), int(month), int(day)]


def split_date_with_edited_date_string(date_string):
    # input a string of the form dd-mm-yyyy
    # output a list of integers [yyyy, mm, dd]
    day = date_string[0:2]
    month = date_string[3:5]
    year = date_string[6:10]
    if day[0] == '0':
        day == day[1]
    if month[0] == '0':
        month == month[1]
    return [int(year), int(month), int(day)]


def get_date_string_with_splitted_date(splitted_date):
    # input a list of integers [yyyy, mm, dd]
    # output a string of the form dd-mm-yyyy
    year = splitted_date[0]
    month = splitted_date[1]
    day = splitted_date[2]

    if day < 10:
        if month < 10:
            return "0{}-0{}-{}".format(day, month, year)
        else:
            return "0{}-{}-{}".format(day, month, year)

    else:
        if month < 10:
            return "{}-0{}-{}".format(day, month, year)
        else:
            return "{}-{}-{}".format(day, month, year)


def get_weekday_with_date(date):
    return date.weekday()


def get_edited_date_string_with_date(date):
    splitted_date = split_date(date)
    date_string = get_date_string_with_splitted_date(splitted_date)
    return date_string


def get_date_with_edited_string(date_string):
    splitted_date = split_date_with_edited_date_string(date_string)
    year = splitted_date[0]
    month = splitted_date[1]
    day = splitted_date[2]
    return datetime.date(year, month, day)


def get_next_date(date):
    return date + datetime.timedelta(days=1)


def get_hour_and_minute() -> list:
    # return a list of current hour and minute
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    return [hour, minute]
# ______________________________________________________________________________________________________________________
#                                                   Helper Functions
# ______________________________________________________________________________________________________________________
def get_weekly_income(all_raw_data):
    # return weekly income (type: int)
    return convert_gspread_string_to_float(all_raw_data[weekly_income_row_index - 1][weekly_income_col_index - 1])


def get_weekend_counter(all_raw_data):
    # return weekly income (type: int)
    return str(all_raw_data[weekend_counter_row_index - 1][weekend_counter_col_index - 1])


def fill_in_initial_daily_row(row, date, weekend_counter, weekly_income):
    initial_spending = 0

    if get_weekday_with_date(date) == MONDAY:
        fill_in_initial_weekly_balance(row)
        update_last_weekly_balance_row_index(row)

    if weekend_counter == "no":
        if get_weekday_with_date(date) == SATURDAY or get_weekday_with_date(date) == SUNDAY:
            daily_initial_balance = 0
            fill_in_daily_row(row, date, initial_spending, daily_initial_balance)
        else:
            daily_initial_balance = round(weekly_income / 5, 2)
            fill_in_daily_row(row, date, initial_spending, daily_initial_balance)
            add_to_last_weekly_balance(daily_initial_balance)
    else:
        daily_initial_balance = round(weekly_income / 7, 2)
        add_to_last_weekly_balance(daily_initial_balance)
        fill_in_daily_row(row, date, initial_spending, daily_initial_balance)


def fill_in_daily_gap(all_raw_data, date):
    nb_rows = get_nb_rows(all_raw_data)
    last_date = get_last_row_date(all_raw_data)
    current_date = last_date
    weekly_income = get_weekly_income(all_raw_data)
    weekend_counter = get_weekend_counter(all_raw_data).lower()
    while current_date != date:
        current_date = get_next_date(current_date)
        nb_rows += 1
        fill_in_initial_daily_row(nb_rows, current_date, weekend_counter, weekly_income)


# new code from ipad
def update_values_last_daily_row(all_raw_data, amount):
    last_row_index = get_nb_rows(all_raw_data)
    last_row = all_raw_data[last_row_index - 1]

    last_daily_spending = convert_gspread_string_to_float(last_row[daily_spending_sheet_spending_index - 1])
    last_daily_balance = convert_gspread_string_to_float(last_row[daily_spending_sheet_balance_index - 1])

    new_daily_spending = last_daily_spending + amount
    new_daily_balance = last_daily_balance - amount

    updated_values_list = [[new_daily_spending, new_daily_balance]]

    dailly_spending_to_update.values_update('Blad1!C{}'.format(last_row_index),
                                            params={'valueInputOption': 'RAW'},
                                            body={'values': updated_values_list}
                                            )


def update_last_weekly_balance_row_index(new_index):
    daily_spending_sheet.update_cell(2, daily_spending_sheet_last_weekly_balance_row_index, new_index)


def get_last_weekly_balance_row():
    return int(daily_spending_sheet.cell(2, daily_spending_sheet_last_weekly_balance_row_index).value)


def update_last_weekly_balance(new_balance):
    last_weekly_balance_row = get_last_weekly_balance_row()
    daily_spending_sheet.update_cell(last_weekly_balance_row, daily_spending_sheet_weekly_balance_index, new_balance)


def get_last_weekly_balance():
    last_weekly_balance_row = get_last_weekly_balance_row()
    return daily_spending_sheet.cell(last_weekly_balance_row, daily_spending_sheet_weekly_balance_index).value


def add_to_last_weekly_balance(amount_to_add):
    last_weekly_balance_amout = convert_gspread_string_to_float(get_last_weekly_balance())
    new_last_weekly_balance_amout = last_weekly_balance_amout + amount_to_add
    update_last_weekly_balance(new_last_weekly_balance_amout)


def subtract_from_last_weekly_balance(amount_to_subtract):
    last_weekly_balance_amout = convert_gspread_string_to_float(get_last_weekly_balance())
    new_last_weekly_balance_amout = last_weekly_balance_amout - amount_to_subtract
    update_last_weekly_balance(new_last_weekly_balance_amout)


def get_total_balance():
    return daily_spending_sheet.cell(total_balance_row_index, total_balance_column_index).value


def daily_spend(amount):
    date = get_todays_date()
    all_raw_data = get_all_raw_data()
    fill_in_daily_gap(all_raw_data, date)
    all_raw_data = get_all_raw_data()
    update_values_last_daily_row(all_raw_data, amount)
    subtract_from_last_weekly_balance(amount)


def get_savings_multiplier():
    return daily_spending_sheet.cell(2, savings_multiplier_column_index).value


def calculate_amount_saved():
    last_weekly_balance = convert_gspread_string_to_float(get_last_weekly_balance())
    savings_multiplier = convert_gspread_string_to_float(get_savings_multiplier())
    return last_weekly_balance * savings_multiplier


def update_last_savings_cell():
    last_weekly_balance_row = get_last_weekly_balance_row()
    amount_saved = calculate_amount_saved()
    if amount_saved < 0:
        amount_saved = 0
    daily_spending_sheet.update_cell(last_weekly_balance_row, weekly_savings_column_index, amount_saved)
    return amount_saved


def update_weekly_balance(all_raw_data):
    last_weekly_balance_row = get_last_weekly_balance_row()
    counter = -1
    result = 0
    while counter < 6 and (last_weekly_balance_row + counter) < len(all_raw_data):
        daily_balance_string = all_raw_data[last_weekly_balance_row + counter][daily_spending_sheet_balance_index - 1]
        daily_balance = convert_gspread_string_to_float(daily_balance_string)
        result += daily_balance
        counter += 1

    daily_spending_sheet.update_cell(last_weekly_balance_row, daily_spending_sheet_weekly_balance_index, result)


def automatic_daily_row_fill_in():
    date = get_todays_date()
    all_raw_data = get_all_raw_data()
    fill_in_daily_gap(all_raw_data, date)
# ____________________________________________________________________________________________________________________
#                                                   Discord
# ____________________________________________________________________________________________________________________

Client = discord.Client()  # Initialise Client
client = commands.Bot(command_prefix="!")  # Initialise client bot


@client.event
async def on_ready():
    print("Bot is online and connected to Discord")


def is_convertible_to_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def is_valid_score_input(text_message):
    text_split = text_message.split()
    if len(text_split) != 2:
        return False
    else:
        amount = text_split[1]
        if not is_convertible_to_float(amount):
            return False
        else:
            return True


@client.command()
async def spend(ctx):
    recieved_message = ctx.message.content
    print(recieved_message)
    if is_valid_score_input(recieved_message):
        await ctx.send("updating...")
        # try:
        refresh_google_tokens()
        amount = float(recieved_message.split()[1])
        daily_spend(amount)
        await ctx.send("updated")
        # except:
        #     await ctx.send("Something went wrong.")
    else:
        await ctx.send("Not a valid argument for !spend.")


@client.command()
async def weekly(ctx):
    try:
        refresh_google_tokens()
        weekly_balance = get_last_weekly_balance()
        await ctx.send("Weekly balance: €{}".format(weekly_balance))
    except:
        await ctx.send("Something went wrong.")


@client.command()
async def total(ctx):
    try:
        refresh_google_tokens()
        total_balance = get_total_balance()
        await ctx.send("Total balance: €{}".format(total_balance))
    except:
        await ctx.send("Something went wrong.")


@client.command()
async def save(ctx):
    amount_saved = update_last_savings_cell()
    await ctx.send("Amount saved this week: `€ {}`".format(amount_saved))


@client.command()
async def update(ctx):
    all_raw_data = get_all_raw_data()
    update_weekly_balance(all_raw_data)
    await ctx.send("Done")


async def auto_day_fill_in():
    print("Starting loop")
    await client.wait_until_ready()


    while True:
        now = get_hour_and_minute()
        hour = now[0]
        minute = now[1]
        print(hour)
        if hour == 10 and minute == 47:
            print("Auto filling in day.")
            automatic_daily_row_fill_in()
            print("going to sleep")
            await asyncio.sleep(20 * 60 * 60)  # sleeps 20 hours

        else:
            print("sleep for 56 secs...")
            await asyncio.sleep(56)


client.loop.create_task(auto_day_fill_in())
client.run(discord_bot_private_key)
