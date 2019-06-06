from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.actionbar import ActionBar
import json
import hashlib
import os
import pygsheets

#burger

class WeatherRoot(ScreenManager, BoxLayout):
    pass


class RegisterPage(BoxLayout, Screen):
    username_input = ObjectProperty()
    password_input = ObjectProperty()
    email_input = ObjectProperty()
    validation = ObjectProperty()

    def register_validation(self):
        f = open("data.json", "r", encoding="utf-8")
        data = json.load(f)
        idLst = []
        f.close()
        for users in data['users']:
            idLst.append(users)
        for id in idLst:
            if (self.username_input.text or self.password_input.text or self.email_input.text) == "":
                self.validation.text = "Form not completed"
            elif (self.username_input.text == data['users'][id]['username']) or (self.email_input.text == data['users'][id]['email']):
                self.validation.text = "Username or Email is taken"
            else:
                self.register(idLst, data)

    def register(self, idLst, data):
        id = str(int(idLst[-1]) + 1)
        salt = "yousaltybro"
        passHash = hashlib.md5((salt + self.password_input.text).encode("utf-8")).hexdigest()
        data['users'][id] = {"username": self.username_input.text, "password_hash": passHash,
                             "email": self.email_input.text, "recent_searches_METAR": [], "recent_searches_ICAO": []}
        with open("temp.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        f.close()
        os.remove("data.json")
        os.rename("temp.json", "data.json")
        self.validation.text = "Registration Complete"
        self.password_input.text = ""
        self.email_input.text = ""
        self.username_input.text = ""


class LoginPage(BoxLayout, Screen):
    username_input = ObjectProperty()
    password_input = ObjectProperty()
    validation = ObjectProperty()

    def validate(self):
        f = open("data.json", "r", encoding="utf-8")
        data = json.load(f)
        idLst, usrlst = [], []
        for id in data['users']:
            idLst.append(id)
            usrlst.append(data['users'][id]['username'])
        if (self.username_input.text or self.password_input.text) == "":
            self.validation.text = "Form not completed"
        elif (self.username_input.text not in usrlst):
            self.validation.text = "User doesn't exist"
        else:
            self.login(usrlst, idLst, data)

    def login(self, usrLst, idLst, data):
        users = dict(zip(usrLst, idLst))
        usrinfo = data['users'][users[self.username_input.text]]
        salt = "yousaltybro"
        passHash = hashlib.md5((salt + self.password_input.text).encode("utf-8")).hexdigest()
        if usrinfo['password_hash'] == passHash:
            self.manager.current = 'AddLocation'
        else:
            self.validation.text = "Password is wrong"


class AddLocationForm(BoxLayout, Screen):
    search_input = ObjectProperty()
    search_results = ObjectProperty()
    recent_search_one = ObjectProperty()
    recent_search_two = ObjectProperty()
    recent_search_three = ObjectProperty()

    def search_location(self):
        search_template = "https://avwx.rest/api/metar/{}?options=summary&format=json&onfail=cache"
        search_url = search_template.format(self.search_input.text)
        request = UrlRequest(search_url, self.found_location)
        print(f"request = {request}")

    def found_location(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        print(data)
        toAdd = []
        raw = data['raw'].split()
        summary = data['summary'].split(',')
        print(f"raw = {raw}\nsummary = {summary}")
        for i in summary:
            toAdd.append(i)
        print(toAdd)
        self.search_results.item_strings = toAdd



    def change_val(self, val):
        print("Hello")
        self.search_input.text = val


class ICAOFinder(BoxLayout, Screen):
    search_input = ObjectProperty()
    search_results = ObjectProperty()

    def findICAO(self):
        f = open("airports.csv", encoding="utf-8")
        data = []
        for line in f:
            data_line = line.rstrip().split('\n')
            data_list = data_line[0].split(',')
            data.append(data_list)
        ICAOList = ["Search results are: "]
        counter = 0
        for lst in data:
            if self.search_input.text in lst[1]:
                counter += 1
                ICAOList.append("{} ICAO is {}".format(lst[1], lst[0]))
        ICAOList.insert(0, "Total number of results: {}".format(counter))
        self.search_results.item_strings = ICAOList


class Sample(Screen, BoxLayout):
    pass


class WeatherApp(App):
    pass


if __name__ == "__main__":
    WeatherApp().run()
