import os

from flask import Flask, request
from fbmessenger import BaseMessenger
from fbmessenger.templates import GenericTemplate
from fbmessenger.elements import Text, Button, Element
from fbmessenger import quick_replies
from fbmessenger.attachments import Image, Video
from fbmessenger.thread_settings import (
    GreetingText,
    GetStartedButton,
    PersistentMenuItem,
    PersistentMenu,
    MessengerProfile,
)
import string
import requests
from bs4 import BeautifulSoup

def get_button(ratio):
    return Button(
        button_type='web_url',
        title='facebook {}'.format(ratio),
        url='https://facebook.com/',
        webview_height_ratio=ratio,
    )


def get_element(btn):
    return Element(
        title='Testing template',
        item_url='http://facebook.com',
        image_url='http://placehold.it/300x300',
        subtitle='Subtitle',
        buttons=[btn]
    )

def get_train_status(trainnumber):
    payload = {'TextTrnNo': trainnumber, 'Button1': '', '__VIEWSTATE': ''}
    r = requests.post('https://appiris.infofer.ro/mytrainro.aspx', data=payload)

    soup = BeautifulSoup(r.text, 'html.parser')
    list = []

    for td in soup.find_all('font'):
        list.append(td.get_text())

    if list[0] != 'Trenul nu este în programul curent de circulație.':
        if list[10] == 'Sosit la destinatie':
            status = "The train arrived at the destination at "+list[14]
        else:
            status = "Your train is moving and it has a delay of "+list[16]+" minutes. "+"Next station "+list[22]+"(current station:"+list[12]+")"
    else:
        status = "The train number is incorrect or the train is not in the traveling program :("

    return status

def process_message(message):
    app.logger.debug('Message received: {}'.format(message))

    if 'attachments' in message['message']:
        if message['message']['attachments'][0]['type'] == 'location':
            app.logger.debug('Location received')

            qr1 = quick_replies.QuickReply(title='start over', payload='START_OVER')
            qrs = quick_replies.QuickReplies(quick_replies=[qr1])

            response = Text(text='{}: lat: {}, long: {}'.format(
                message['message']['attachments'][0]['title'],
                message['message']['attachments'][0]['payload']['coordinates']['lat'],
                message['message']['attachments'][0]['payload']['coordinates']['long']
            ), quick_replies=qrs)
            return response.to_dict()

    if 'text' in message['message']:
        msg = message['message']['text'].lower()
        qr1 = quick_replies.QuickReply(title='start over', payload='START_OVER')
        qrs = quick_replies.QuickReplies(quick_replies=[qr1])

        if msg.isdigit():
            st = get_train_status(msg)
            qr1 = quick_replies.QuickReply(title='track another train', payload='track')
            qrs = quick_replies.QuickReplies(quick_replies=[qr1])
            response = Text(text=st, quick_replies=qrs)
        else:
            response = Text(text='Sorry didn\'t understand that: {}.'.format(msg), quick_replies=qrs)

        if 'get started' in msg or 'start over' in msg:
            qr1 = quick_replies.QuickReply(title='train location', payload='QUICK_REPLY_PAYLOAD')
            qr2 = quick_replies.QuickReply(title='train station', payload='train station')
            qr3 = quick_replies.QuickReply(title='help', payload='QUICK_REPLY_PAYLOAD')
            qr4 = quick_replies.QuickReply(title='start over', payload='START_OVER')
            qrs = quick_replies.QuickReplies(quick_replies=[qr1, qr2, qr3, qr4])
            response = Text(text='Hi, welcome to travelrr bot. Travelrr bot helps people to use Romanian Railways service more easily. Choose one of the operations from below. Have fun traveling! 🚂', quick_replies=qrs)
        if 'help' in msg:
            qr1 = quick_replies.QuickReply(title='start over', payload='START_OVER')
            qr2 = quick_replies.QuickReply(title='cannot find train no.', payload='trainnohelp')
            qrs = quick_replies.QuickReplies(quick_replies=[qr1, qr2])
            response = Text(text='Select one of the options below. In case you got stuck you can press \'Start over\' ', quick_replies=qrs)
        if 'train location' in msg or 'track another train' in msg:
            qr1 = quick_replies.QuickReply(title='help', payload='help')
            qrs = quick_replies.QuickReplies(quick_replies=[qr1])
            response = Text(text='Please enter the number of your train.', quick_replies=qrs)
        if 'train station' in msg:
            qr1 = quick_replies.QuickReply(title='Location', content_type='location')
            qrs = quick_replies.QuickReplies(quick_replies=[qr1])
            response = Text(text='Choose your location to get the nearest train station. 🗺', quick_replies=qrs)
        if 'cannot find train no.' in msg:
            response = Image(url='http://i68.tinypic.com/fdudfn.png')

        return response.to_dict()


class Messenger(BaseMessenger):
    def __init__(self, page_access_token):
        self.page_access_token = page_access_token
        super(Messenger, self).__init__(self.page_access_token)

    def message(self, message):
        action = process_message(message)
        res = self.send(action, 'RESPONSE')
        app.logger.debug('Response: {}'.format(res))

    def delivery(self, message):
        pass

    def read(self, message):
        pass

    def account_linking(self, message):
        pass

    def postback(self, message):
        payload = message['postback']['payload']
        if 'start' in payload:
            txt = ('Hey, let\'s get started! Try sending me one of these messages: '
                   'text, image, video, "quick replies", '
                   'webview-compact, webview-tall, webview-full')
            self.send({'text': txt}, 'RESPONSE')
        if 'help' in payload:
            self.send({'text': 'A help message or template can go here.'}, 'RESPONSE')

    def optin(self, message):
        pass

    def init_bot(self):
        self.add_whitelisted_domains('https://facebook.com/')
        greeting = GreetingText(text='Welcome to the fbmessenger bot demo.')
        self.set_messenger_profile(greeting.to_dict())

        get_started = GetStartedButton(payload='start')
        self.set_messenger_profile(get_started.to_dict())

        menu_item_1 = PersistentMenuItem(
            item_type='postback',
            title='Help',
            payload='help',
        )
        menu_item_2 = PersistentMenuItem(
            item_type='web_url',
            title='Messenger Docs',
            url='https://developers.facebook.com/docs/messenger-platform',
        )
        persistent_menu = PersistentMenu(menu_items=[
            menu_item_1,
            menu_item_2
        ])

        res = self.set_messenger_profile(persistent_menu.to_dict())
        app.logger.debug('Response: {}'.format(res))

#os.environ['FB_PAGE_TOKEN'] = 'EAAEVhxYs8zoBAAgHudQk4qJSwESPMYX0mjfqae14mUafFo7ezrJaoWcMHm2Pqbf7Oe69JfQvMzq18bhrQm2dZCWEZBFdvaPzcCNk3OIyINDM2UA8qm3hIlrxkr6fgean01yrLB3jW6vj39jaZBTyUXeiM7YnCRBubD7HzJQ0MtZCCU6IsvFr'
#os.environ['FB_VERIFY_TOKEN'] = 'hello'

app = Flask(__name__)
app.debug = True
messenger = Messenger(os.environ.get('FB_PAGE_TOKEN'))


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == os.environ.get('FB_VERIFY_TOKEN'):
            if request.args.get('init') and request.args.get('init') == 'true':
                messenger.init_bot()
                return ''
            return request.args.get('hub.challenge')
        raise ValueError('FB_VERIFY_TOKEN does not match.')
    elif request.method == 'POST':
        messenger.handle(request.get_json(force=True))
    return ''


if __name__ == '__main__':
    app.run()