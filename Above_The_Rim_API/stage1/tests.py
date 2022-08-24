import asyncio
import json
import random
from hstest import FlaskTest, CheckResult, WrongAnswer
from hstest import dynamic_test
from hstest.dynamic.security.exit_handler import ExitHandler
from pip._vendor import requests
from bs4 import BeautifulSoup
import sqlite3
import os


class SQLite3Test:

    """It's recommended to keep the sequence:
    1. Create object SQLite3Check
    2. Check is file exists
    3. Establish connection
    4. Check is table exists
    5. Check are columns exists
    6. Do the rest of tests on tables: is column primary key, not null

    To do tests: is unique and is foreign key"""

    cursor_message = f"There is no cursor to connection."  # Is it proper message?
    no_table_message = f"There is no table you are looking for."

    def __init__(self, file_name):  # file_name -> string
        self.file_name = file_name
        self.conn = None
        self.cursor = None

    def is_file_exist(self):
        if not os.path.exists(self.file_name):
            raise WrongAnswer(f"The file '{self.file_name}' does not exist or is outside of the script directory.")

    def connect(self):
        ans = self.is_file_exist()
        if ans:
            return ans
        try:
            self.conn = sqlite3.connect(self.file_name)
            self.cursor = self.conn.cursor()
        except sqlite3.OperationalError as err:
            raise WrongAnswer(f"DataBase {self.file_name} may be locked. An error was returned when trying to connect: {err}.")

    def close(self):
        try:
            self.conn.close()
        except AttributeError:
            raise WrongAnswer(self.cursor_message)

    def run_query(self, query):
        try:
            lines = self.cursor.execute(f"{query}")
        except AttributeError:
            raise WrongAnswer(self.cursor_message)
        except sqlite3.OperationalError as err:
            self.close()
            raise WrongAnswer(f"Error '{err}' occurred while trying to read from database '{self.file_name}'.")
        except sqlite3.DatabaseError as err:
            self.close()
            raise WrongAnswer(f"Error '{err}' occurred while trying to read from database '{self.file_name}'.")
        return lines

    def is_table_exist(self, name):  # table name -> string
        lines = self.run_query(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{name}';").fetchall()
        if lines[0][0] == 0:
            self.close()
            raise WrongAnswer(f"There is no table named '{name}' in database {self.file_name}")

    def number_of_records(self, name, expected_lines):   # table name -> string, expected_lines -> integer
        lines = self.run_query(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        if lines != expected_lines:
            self.close()
            raise WrongAnswer(f"Wrong number of records in table {name}. Expected {expected_lines}, found {lines}")

    def is_column_exist(self, name, names):  # table name -> string, column names -> list of strings for all columns, or list with one string for one column
        lines = self.run_query(f'select * from {name}').description
        if len(names) != 1:
            if sorted(names) != sorted([line[0] for line in lines]):
                self.close()
                raise WrongAnswer(f"There is something wrong in table {name}. Found column names: {[line[0] for line in lines]}. Expected {names}'")
        else:
            if not any([names[0] == c_name for c_name in [line[0] for line in lines]]):
                self.close()
                raise WrongAnswer(f"There is something wrong in table {name}. Found column names: {[line[0] for line in lines]}. Expected to find '{names[0]}'")

    def table_info(self, name, column, attribute):   # table name -> string, column name -> string, attr ("PK" Primary Key; "NN" Not null)
        lines = self.run_query(f"PRAGMA table_info({name})").fetchall()
        if column not in [line[1] for line in lines]:
            raise WrongAnswer(f"There is no column {column}.")
        for line in lines:
            if attribute == "PK":
                if line[1] == column and line[5] != 1:
                    self.close()
                    raise WrongAnswer(f"There is no PRIMARY KEY parameter in {name} on column {column}.")
            elif attribute == "NN":
                if line[1] == column and line[3] != 1:
                    raise WrongAnswer(f"There is no NOT NULL parameter in {name} on column {column}.")

    def is_unique(self, name, column):  # table name -> string, column name -> string
        lines = self.run_query(f"SELECT inf.name FROM pragma_index_list('{name}') as lst, pragma_index_info(lst.name) as inf WHERE lst.[unique] = 1;").fetchall()
        if not any([column in line for line in lines]):
            raise WrongAnswer(f"There is no UNIQUE parameter in {name} on column {column}.")
        return True

    def is_foreign_key(self, name, column):  # table name -> string, column name -> string
        lines = self.run_query(f"SELECT * FROM pragma_foreign_key_list('{name}');").fetchall()
        if not any([column in line for line in lines]):
            raise WrongAnswer(f"There is no FOREIGN KEY parameter in {name} on column {column}.")
        return True


class FlaskProjectTest(FlaskTest):
    source = 'basketball_API'

    def __init__(self, source_name: str = ''):
        super().__init__(source_name)

    def check_json(self, output_dict, expect_dict):
        if len(output_dict) != len(expect_dict):
            return True
        for key in expect_dict.keys():
            if key not in output_dict.keys():
                return True
            if expect_dict[key] != output_dict[key]:
                return True
        return False

    async def test_home_page(self):
        r = requests.get(self.get_url())
        if r.status_code != 200:
            raise WrongAnswer("Home page should return code 200.")
        content = r.content.decode('UTF-8')
        if content.lower().count("<h1>") != 1 or content.lower().count("</h1>") != 1:
            raise WrongAnswer("There should be one tag <h1> and one tag </h1>.")
        soup = BeautifulSoup(content, 'html.parser')
        list_all_h1 = soup.find_all('h1')
        if 'Welcome to the "Above the Rim" API!' not in list_all_h1[0].text:
            raise WrongAnswer('There is no welcome text inside the tag <h1>: Welcome to the "Above the Rim" API!')

    async def test_random_page(self):
        r = requests.get("/".join([self.get_url(), ''.join(random.choice("abcdefghijk") for i in range(5))]))
        if r.status_code != 404:
            raise WrongAnswer("Not existing page should return code 404.")
        content = r.content.decode('UTF-8')
        try:
            content = json.loads(content)
        except json.decoder.JSONDecodeError:
            raise WrongAnswer('Request do not return JSON data.')
        #  expected = json.loads(json.dumps({"success": False, "data": "Wrong address"}))
        expected = {"success": False, "data": "Wrong address"}

        if self.check_json(content, expected):
            raise WrongAnswer(f'Wrong JSON format. \nExpected\n{dict(sorted(expected.items()))}, \nFound:\n{dict(sorted(content.items()))}')

    @dynamic_test(order=1)
    def test1(self):
        ExitHandler.revert_exit()
        print("Checking Home Page.")
        asyncio.get_event_loop().run_until_complete(self.test_home_page())
        return CheckResult.correct()

    @dynamic_test(order=2)
    def test2(self):
        ExitHandler.revert_exit()
        print("Checking not existing page.")
        asyncio.get_event_loop().run_until_complete(self.test_random_page())
        return CheckResult.correct()

    @dynamic_test(order=2)
    def test3(self):
        ExitHandler.revert_exit()
        db_name = "db.sqlite3"
        table = "teams"
        columns = ["id", "short", "name"]
        print("Checking database.")
        database = SQLite3Test(db_name)
        database.connect()
        database.is_file_exist()
        database.is_table_exist(table)
        database.is_column_exist(table, columns)
        database.table_info(table, columns[0], "PK")
        database.table_info(table, columns[2], "NN")
        database.table_info(table, columns[1], "NN")
        database.is_unique(table, columns[2])
        database.is_unique(table, columns[1])
        database.close()
        return CheckResult.correct()


if __name__ == '__main__':
    FlaskProjectTest().run_tests()
