import asyncio
import json
import random
from hstest import FlaskTest, CheckResult, WrongAnswer
from hstest import dynamic_test
from hstest.dynamic.security.exit_handler import ExitHandler
from pip._vendor import requests
from bs4 import BeautifulSoup


class FlaskProjectTest(FlaskTest):
    source = 'basketball_API'

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
    def test1(self):
        ExitHandler.revert_exit()
        print("Checking not existing page.")
        asyncio.get_event_loop().run_until_complete(self.test_random_page())
        return CheckResult.correct()


if __name__ == '__main__':
    FlaskProjectTest().run_tests()
