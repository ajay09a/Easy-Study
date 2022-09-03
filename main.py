import os.path
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase
from kivymd.theming import ThemeManager
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import BooleanProperty, DictProperty, ListProperty, NumericProperty, ObjectProperty, \
    OptionProperty, StringProperty
from kivy.graphics import Rectangle, Color

from kivy.uix.floatlayout import FloatLayout
from kivy.lang.builder import Builder
from kivy.core.window import Window

from vidstream import ScreenShareClient
import threading

from kivy.uix.label import Label
import sys
import socket_client
from chat_screen_example import SmoothLabel
from kivymd.uix.filemanager import MDFileManager


# Load ML Library to using a train and a test set
import pandas as pd
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from pandas import set_option,DataFrame



Window.size = (370, 630)


# Detach the DATA to a train and a test set
filename = r'marks.csv'
names = ['java', 'dsa', 'os']
dataframe = read_csv(filename, names=names, delimiter=';')
array = dataframe.values
X = array[:,0:3]
Y = array[:,2]
test_size = 0.33
seed = 7
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size,random_state=seed)
model = LogisticRegression()
model.fit(X_train, Y_train)
result = model.score(X_test, Y_test)

# machine learning part
# Receive data user input & formatting it
def user_report(java, dsa, os):
    Java = float(java)
    DSA = float(dsa)
    OS = float(os)

    user_report_data = {
        'Java': Java,
        'DSA': DSA,
        'OS': OS,

    }
    report_data = pd.DataFrame(user_report_data, index=[0])
    return report_data


class Tab(FloatLayout, MDTabsBase):
    pass


class ChatScreen(Screen):
    # A screen that display messages with a user.

    text = StringProperty()
    image = ObjectProperty()
    active = BooleanProperty(defaultvalue=False)




class MainApp(MDApp):
    chat_layout = ObjectProperty(None)

    def build(self):
        """self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.primary_hue = '800'
        return Builder.load_file('main.kv')"""
        pass

    # theme manager
    def show_theme_picker(self):
        '''Display a dialog window to change app's color and theme.'''
        theme_dialog = MDThemePicker()
        theme_dialog.open()

    def demo(self):
        print(self.screen.ids.toolbar.right_action_items[1])

    # Screen manager
    def change_screen(self, screen_name, curr=None, title=None):
        self.root.ids.screen_manager.current = screen_name
        if curr is not None:
            self.root.ids.screen_manager.transition.direction = 'right'
        else:
            self.root.ids.screen_manager.transition.direction = 'left'
        if title is not None:
            self.set_title(title)

    """def btn(self):
        msg = self.root.ids.new_msg.text
        print(msg)
        self.root.ids.new_msg.text = ''"""

    def set_title(self, title):
        self.root.ids.toolbar_chat_screen.title = title

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        '''Called when switching tabs.
        :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
        :param instance_tab: <__main__.Tab object>;
        :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
        :param tab_text: text or name icon of tab;
        '''
    def btn(self):
        pass

    # user login page
    # to read the file and give user an empty textbox
    def click(self):
        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt", "r") as f:
                d = f.read().split(",")
                ports = d[0]
                ips = d[0]
                user = d[0]
                print(d)

        else:
            ports = " "
            ips = " "
            user = " "

    # to write on text file after getting input
    def clicked(self):
        port = self.root.ids.ports.text
        ip = self.root.ids.ips.text
        username = self.root.ids.user.text

        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")

        Clock.schedule_once(self.connect, 1)

    # to change the text of ip port and username by every login
    def change_text(self):
        self.root.ids.information.text = "Attempting to join " + self.root.ids.ips.text + " " + self.root.ids.ports.text + " as " + self.root.ids.user.text
        # self.root.ids.information.text_size = (self.root.ids.information.width*13, None)

    # connection between user and server
    def connect(self, _):
        port = int(self.root.ids.ports.text)
        ip = self.root.ids.ips.text
        username = self.root.ids.user.text

        if not socket_client.connect(ip, port, username, self.show_error):
            return

    def show_error(self):
        self.root.ids.information.text = "fail error"

    # update chat after every message
    def update_chat_history(self, message):
        # First add new line and message itself
        self.root.ids.chat_history.text += '\n' + message

    def start_chat(self):
        # To be able to send message on Enter key, we want to listen to keypresses
        Window.bind(on_key_down=self.on_key_down)


        # The problem here is that 'self.new_message.focus = True' does not work when called directly,
        # so we have to schedule it to be called in one second
        # The other problem is that schedule_once() have no ability to pass any parameters, so we have
        # to create and call a function that takes no parameters
        Clock.schedule_once(self.focus_text_input, 1)

        # we have to start listening for new messages after we create this layout
        socket_client.start_listening(self.incoming_message, self.show_error)

    # send message on pressing click button
    def send(self):
        if self.root.ids.new_msg.text:
            # calculate max allowable width in the BoxLayout
            max_width = (self.root.ids.chat_layout.width - self.root.ids.chat_layout.spacing) * 0.75

            # specify font and font_size (so that the CoreLabel uses the same)
            self.root.ids.chat_layout.add_widget(
                SmoothLabel.create_sized_label(text=self.root.ids.new_msg.text, max_width=max_width,
                                               font_name='Roboto',
                                               font_size=15, pos_hint={'right': 1}))
            self.root.ids.new_msg.text = ""
            self.root.ids.scroll.scroll_y = 0  # make sure last message is visible
        else:
            pass

    # on keyboard button press send message
    def on_key_down(self, instance, keyboard, keycode, text, modifiers):

        # But we want to take an action only when Enter key is being pressed, and send a message
        if keycode == 40:
            self.send_message(None)

    # send message on clicking enter on keyboard
    def send_message(self, _):

        # Get message text and clear message input field
        message = self.root.ids.new_msg.text
        self.root.ids.new_msg.text = ''

        # If there is any message - add it to chat history and send to the server
        if message:
            self.update_chat_history(f'{self.root.ids.user.text}: \n{message}')
            socket_client.send(message)

        # to schedule for refocusing to input field
        Clock.schedule_once(self.focus_text_input, 0.1)


    # Sets focus to text input field
    def focus_text_input(self, _):
        self.root.ids.new_msg.focus = True

    # Passed to sockets client, get's called on new message
    def incoming_message(self, username, message):
        self.update_chat_history(f'{username}: \n{message}')

    # to predict the report of student using machine learning
    def predict(self):
        input_1 = self.root.ids.input_1.text
        input_2 = self.root.ids.input_2.text
        input_3 = self.root.ids.input_3.text

        user_result_input = user_report(input_1, input_2, input_3)

        user_result_model = model.predict(user_result_input)

        output = ''
        self.root.ids.output_text_good.text = ''
        self.root.ids.output_text_bad.text = ''

        if user_result_model[0] == 0:
            output = 'You are doing well. Keep it going.'
            self.root.ids.output_text_good.text = output

        else:
            output = 'Need more improvement!'
            self.root.ids.output_text_bad.text = output

    def start_sharing(self):
        sender = ScreenShareClient('192.168.1.4', 9999)

        t = threading.Thread(target=sender.start_stream())
        t.start()

        while input("") != 'STOP':
            continue

        sender.start_stream()

if __name__ == '__main__':
    MainApp().run()
