import gspread
from oauth2client.service_account import ServiceAccountCredentials
import discord
from discord.ext import commands
import os
import datetime



# get discord version should be version 0.0.2
print(discord.__version__)


# static variables
sheet_date_index = 1
sheet_day_name_index = 2
daily_spending_sheet_spending_index = 3
daily_spending_sheet_balance_index = 4
daily_spending_sheet_weekly_balance_index = 5
daily_spending_sheet_last_weekly_balance_row_index = 10

weekly_income_row_index = 2
weekly_income_col_index = 7
weekend_counter_row_index = 2
weekend_counter_col_index = 9


MONDAY = 0
SATURDAY = 5
SUNDAY = 6

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


# ______________________________________________________________________________________________________________________
#                                                   Spreadsheets
# ______________________________________________________________________________________________________________________
def refresh_daily_credentials():
    # this function refreshes the credentials to be able to edit the spreadsheet
    global scope, creds, client_gspread
    global daily_spending_sheet
    print("Refreshing credentials ...")
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        }, scope)
    client_gspread = gspread.authorize(creds)
    daily_spending_sheet = client_gspread.open("daily_spending").sheet1
    print("Refreshed credentials for daily balance.")


def get_nb_rows(spreadsheet):
    # return the number of filled in rows in integer type
    return len(spreadsheet.col_values(1))


def fill_in_date_in_row(spreadsheet, row, date):
    # fill in the date (type: date) in the row of spreadsheet
    date_string = get_edited_date_string_with_date(date)
    weekday_string = weekday_list[get_weekday_with_date(date)]
    spreadsheet.update_cell(row, sheet_date_index, date_string)
    spreadsheet.update_cell(row, sheet_day_name_index, weekday_string)


def fill_in_daily_spending_in_row(row, spending_amount):
    # fill in the spending amount (type: int) in the row of daily_spending spreadsheet
    daily_spending_sheet.update_cell(row, daily_spending_sheet_spending_index, spending_amount)


def fill_in_daily_balance_in_row(row, balance):
    # fill in the balance (type: int) in the row of daily_spending spreadsheet
    daily_spending_sheet.update_cell(row, daily_spending_sheet_balance_index, balance)


def fill_in_daily_row(row, date, spending_amount, balance):
    fill_in_date_in_row(daily_spending_sheet, row, date)
    fill_in_daily_spending_in_row(row, spending_amount)
    fill_in_daily_balance_in_row(row, balance)


def fill_in_weekly_balance_in_row(row, balance):
    weekly_balance_sheet.update_cell(row, daily_spending_sheet_balance_index, balance)


def fill_in_weekly_row(row, date, balance):
    fill_in_date_in_row(weekly_balance_sheet, row, date)
    fill_in_weekly_balance_in_row(row, balance)


def get_date_from_spreadsheet_row(spreadsheet, row):
    date_string = spreadsheet.cell(row, sheet_date_index).value
    return get_date_with_edited_string(date_string)

def fill_in_initial_weekly_balance(row):
    daily_spending_sheet.update_cell(row, daily_spending_sheet_weekly_balance_index, 0)


def get_last_row_date(spreadsheet):
    nb_rows = get_nb_rows(spreadsheet)
    if nb_rows > 1:
        return get_date_from_spreadsheet_row(spreadsheet, nb_rows)
    else:
        return None


def convert_gspread_string_to_float(string):
    new_string = string.replace(',', '.')
    return float(new_string)
# ______________________________________________________________________________________________________________________
#                                                   Dates
# ______________________________________________________________________________________________________________________
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


def get_weekday_with_string(date_string):
    # input a string of the form dd-mm-yyyy
    # output an integer where 0 is monday, 1 is tuesday ...
    splitted_date = split_date_with_edited_date_string(date_string)
    year = splitted_date[0]
    month = splitted_date[1]
    day = splitted_date[2]
    date = datetime.date(year, month, day)
    return date.weekday()


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
# ______________________________________________________________________________________________________________________
#                                                   Helper Functions
# ______________________________________________________________________________________________________________________
def get_weekly_income():
    # return weekly income (type: int)
    return convert_gspread_string_to_float(daily_spending_sheet.cell(weekly_income_row_index, weekly_income_col_index).value)


def get_weekend_counter():
    # return weekly income (type: int)
    return str(daily_spending_sheet.cell(weekend_counter_row_index, weekend_counter_col_index).value)


def fill_in_initial_daily_row(row, date, weekend_counter, weekly_income):
    initial_spending = 0

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

    if get_weekday_with_date(date) == MONDAY:
        fill_in_initial_weekly_balance(row)
        update_last_weekly_balance_row_index(row)



def fill_in_daily_gap(date):
    nb_rows = get_nb_rows(daily_spending_sheet)
    last_date = get_last_row_date(daily_spending_sheet)
    current_date = last_date
    weekly_income = get_weekly_income()
    weekend_counter = get_weekend_counter().lower()
    while current_date != date:
        current_date = get_next_date(current_date)
        nb_rows += 1
        fill_in_initial_daily_row(nb_rows, current_date, weekend_counter, weekly_income)


# new code from ipad
def update_last_daily_spending(new_spending):
    last_row_index = get_nb_rows(daily_spending_sheet)
    daily_spending_sheet.update_cell(last_row_index, daily_spending_sheet_spending_index, new_spending)


def update_last_daily_balance(new_balance):
    last_row_index = get_nb_rows(daily_spending_sheet)
    daily_spending_sheet.update_cell(last_row_index, daily_spending_sheet_balance_index, new_balance)


def add_to_last_daily_spending(amount_to_add):
    last_row_index = get_nb_rows(daily_spending_sheet)
    old_spending = convert_gspread_string_to_float(
        daily_spending_sheet.cell(last_row_index, daily_spending_sheet_spending_index).value)
    new_spending = old_spending + amount_to_add
    print("new spending:", new_spending)
    update_last_daily_spending(new_spending)


def subtract_from_last_daily_balance(amount_to_subtract):
    last_row_index = get_nb_rows(daily_spending_sheet)
    old_balance = convert_gspread_string_to_float(
        daily_spending_sheet.cell(last_row_index, daily_spending_sheet_balance_index).value)
    new_balance = old_balance - amount_to_subtract
    print("new balance:", new_balance)
    update_last_daily_balance(new_balance)


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



def daily_spend(amount):
    date = get_todays_date()
    fill_in_daily_gap(date)
    add_to_last_daily_spending(amount)
    subtract_from_last_daily_balance(amount)
    subtract_from_last_weekly_balance(amount)


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
        amount = float(recieved_message.split()[1])
        daily_spend(amount)
        await ctx.send("updated")
        # except:
        #     await ctx.send("Something went wrong.")
    else:
        await ctx.send("Not a valid argument for !spend.")


client.run(discord_bot_private_key)
