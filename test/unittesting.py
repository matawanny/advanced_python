import unittest
import requests

def power(a, b):
    return a**b

class Test(unittest.TestCase):
    def setUp(self):
        response = requests.get("https://jsonplaceholder.typicode.com/users", timeout = 5,  verify=False)
        self.response = response

    def test_power(self):
        res = power(2, 4)
        self.assertEqual(res, 16)

    def test_length_of_user_list(self):
        if(self.response.ok):
            self.assertTrue(len(self.response.json())) == 10
        else:
            self.fail('Could not fetch data withing 5d seconds', 5)

    def test_usr_name(self):
        if(self.response.ok):
            self.assertTrue(self.response.json()[0]['username'] == 'Bret')
        else:
            self.fail('Could not fetch data withing 5d seconds', 5)

if __name__ == '__main__':
    unittest.main()