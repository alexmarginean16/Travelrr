# :steam_locomotive: Travelrr
A Facebook messenger bot that gives train information from Romanian Railways.

Please feel free to contribute to anything for example:
- documentation
- code
- issues
- templates
- fixing bugs
- suggestions

## Requirements

- [Python 3](https://www.python.org/downloads/)
- [ngrok](https://ngrok.com/)

## Environment setup

1. Clone the project
        
        git clone https://github.com/alexmarginean16/Travelrr.git
        cd Travelrr/

2. Create a python virtual environment `python3 -m venv venv`
3. Activate venv: `. /venv/bin/Activate`
4. Install requirements `pip install -r requirements.py`
5. Create a facebook page [here](https://www.facebook.com/pages/creation/).
6. Access [facebook developers](https://developers.facebook.com/) and create a new app, add the messenger product.
7. Go to Messenger > Settings, select your page and get your `Page Access Token`.
9. Run your python application `FB_PAGE_TOKEN=<<yourpagetoken>> FB_VERIFY_TOKEN=<<yourverifytoken>> python app.py`. Where `FB_PAGE_TOKEN` is the access token you copied from facebook app, and `FB_VERIFY_TOKEN` could be whatever you want.
10. Run ngrok on the same port as the python server (usually 5000) `. ngrok http 5000`.
11. On facebook developer website while in your app go to Messenger > Settings and click `Add webhook`. At the webhook URL paste the link ngrok created for the `localhost` tunnel, and the `FB_VERIFY_TOKEN` value you created before. Select every checkbox and click done.
12. Down to "Select a page to subscribe your webhook to the page events" select your desired page and click "subscribe".

Done! :tada:
