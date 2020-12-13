### Factsonfactsbot

------------

Telegram bot that parses news articles for false content and returns a fake news rating. Access the bot [here](https://t.me/factsonfactsbot "here"). 

Alternatively, open up the Telegram app and search for *factsonfactsbot*. It has an accuracy of about 88%. Ideally, I would have had access to 10k+ unique political articles to train the model but I could only access about 2025. 

I have to say thanks to this [article](https://towardsdatascience.com/full-pipeline-project-python-ai-for-detecting-fake-news-with-nlp-bbb1eec4936d "article"). It answered a lot of my questions and gave me a proper reference point/foundation to go about building this.

To run this bot locally, you need to have python3+ on your system. Get it 
[here](https://https://www.python.org/downloads/ "here"). Make sure to add python.exe to your operating system path variables to be able to run python scripts from the command line.

You also need a telegram bot token. Follow the instructions found [here](https://core.telegram.org/bots#6-botfather "here") to create a new bot with its authorization token. 

Navigate into a directory of choice on your system via the terminal and clone this repository by running 

```
git clone https://github.com/olamileke/factsonfactsbot.git
```

navigate into the cloned repository by running

``` 
cd Factsonfactsbot
```

Follow the instructions found [here](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/ "here") to create a virtual environment in which the bot will run.

Activate the virtual environment and install all the python packages needed for the bot to run. Do this by running

```
pip install -r requirements.txt
```

Open up the config.py file located in the application root and set the bot_token option to the authorization token.

Still in the app root in the terminal and with the virtual environment still running, run

```
python app.py
```

Open up the Telegram app to communicate with the bot.


