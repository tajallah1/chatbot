import string
import urllib

# import requests
from flask import Flask, render_template, request
# import aiml
from py2neo import Graph
import aiml
from glob import glob
from gingerit.gingerit import GingerIt

from textblob import TextBlob
app = Flask(__name__)
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))
bot = aiml.Kernel()
def aiml():
    for file in glob("./data/*.aiml"):
        print("learning", file)
        bot.learn(file)
aiml()


@app.route('/')
def login():
    return render_template('login.html')

@app.route("/signup", methods=['POST'])
def getvalue():
    username = request.form.get('username')
    email = request.form.get('email')
    pass1 = request.form.get('pass1')

    graph.run(f"CREATE (n:person{{name: \"{username}\", email: \"{email}\", password: {pass1}}})")
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def login_user():
    email = request.form.get('email')
    pass1 = request.form.get('password')
    print(email,pass1)
    email_ver0 = graph.run(f"MATCH (n:person{{email: \"{email}\", password: {pass1}}}) return n")
    emailver = list(email_ver0)
    print(emailver)
    if emailver:
        return render_template('home.html')
    else:
        return render_template('login.html')

@app.route('/registration')
def about():
    return render_template('registration.html')
@app.route("/home")
def home():
    return render_template("home.html")


def correct_spelling(text):
    parser1 = GingerIt()
    corrected_text = parser1.parse(text)["result"]
    return corrected_text


def getWordnet(word, wn=None):
    wn_definition = ""
    synsets = wn.synsets(word)
    if synsets:
        synset = synsets[0]
        wn_definition = synset.definition()
    return wn_definition


class BeautifulSoup:
    pass


def search_wikipedia(query):
    words = query.split()
    last_two_words = words[-2:]  # Extract last two words
    search_terms = [string.capwords(word) for word in last_two_words]
    encoded_terms = [urllib.parse.quote(term) for term in search_terms]

    line_count = 0

    for term in encoded_terms:
        url = "https://en.wikipedia.org/wiki/" + term
        url_open = request.get(url)
        soup = BeautifulSoup(url_open.content, 'html.parser')
        paragraphs = soup.find_all('p')
        response=""
        if paragraphs:
            for paragraph in paragraphs:
                lines = paragraph.get_text().split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        response = line
                        return response

    return "No information found."

@app.route("/get")
def get_bot_response():
    response = ""
    query = request.args.get('msg')
    # query=correct_spelling(query)
    # print(query)
    # blob = TextBlob(query)
    # s=blob.sentiment.polarity

    # if s >= 0:
    #     a = "Positive"
    # elif s <= 0:
    #     a = "Negative"
    # else:
    #     a = "Neutral"
    # if a == 'Positive':
    #     response = "wow thats amazing"
    # elif a == 'Negative':
    #     response = " oh sad!"
    # else:
    response = bot.respond(query)

    if response:
        print("bot:",response)
    return response

if __name__ == "__main__":
    # app.run()
    app.run(host='0.0.0.0', port='5000')


