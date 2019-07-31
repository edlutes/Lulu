import json
import os
import re
import sqlite3
# EKL  
# string is used to help remove punctuation
# logging is used for debug purposes so that blocked tweets can be seen in docker logs
#  NOTE:  logging will not work unless Dockerfile is modified
# Side NOTE:  Readme.md file refers to server.py which wasn't inlcuded, I took the liberty to work in app.py instead
import string
import logging

from flask import Flask, request, render_template, jsonify

app = Flask(__name__, static_folder="public", template_folder="views")
DBNAME = "database.db"

# Tweet API/functionality below -----------------------------------------------


def create_tweet(tweet, lenient=False):
    """
  If a tweet is allowed, insert it in the DB and return a dict version of it.
  """

    if not lenient:
        # To minimize junk data, avoid inserting an entry if it includes one of
        # the our current terms to avoid.
        # TODO: replace this `pass` with the proper validation

        # NOTE:
        # Any value in storing the reject tweets in a separate db?
        # Would also be nice to only have to process the db once and filter into 
        # a clean/dirty db setup
        # Current setup checks the whole db for filtered words on every GET (every page refresh)
        # if forbidden terms were deleted you could check dirty db and move entries back to clean db
        
        # EKL 
        # Get the parsed/sanitized terms from the tweet
        # Then check the individual words against the list of forbidden words
        parsed_tweet = get_terms_from_tweet(tweet)
        valid_tweet = filter_terms(parsed_tweet)
        if valid_tweet is None:
          # We don't have a valid tweet after censoring
          # nothing to do 
          return 
          # (return error_code)  if we want to alert user with http codes
        # We passed the processing of the tweet, insert into db  
        pass

    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tweets (tweet, username) VALUES (?, ?)", [tweet["tweet"], tweet["username"]]
    )
    conn.commit()
    conn.close()
    return {"tweet": tweet}


def get_terms_from_tweet(tweet):
    """
  Break a tweet into its individual words.

  Each word should:
  * ignore case
  * NOT have special characters like hashtags, commas, periods, or anything
    that would cause us to miss a forbidden term
  """
    # EKL process the tweet
    # strip all punctuation
    # convert all to lowercase
    processed_tweet = tweet['tweet'].translate(str.maketrans('','',string.punctuation)).lower()


    return (processed_tweet.split(" "))

# EKL  This uses the get_terms function that was predefined
# The list of dicts makes this messy and somewhat inefficient  
# This could be simplified by switching to get_terms_list
def filter_terms(terms):
    """
   Run split terms against the list of forbinned terms.

  """
    forbidden_terms = get_terms()
   
    # forbidden_terms is a list of dicts
    for index in range(len(forbidden_terms)):
        for key in forbidden_terms[index]:
          if forbidden_terms[index][key] in terms:
            # we matched a term we should be blocking
            # log it...
            app.logger.warning("Blocked tweet:")
            app.logger.warning(terms)
            return None

    # If we fall to here all terms are "safe"
    return terms


def get_tweets():
    """
  Fetch tweets from DB and return a list of dicts, as long as no terms are detected.
  """
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute("SELECT tweet, username FROM tweets")
    rows = c.fetchall()
    conn.commit()
    conn.close()


    # NOTE:
    # With enough experimentation I think all the forbidden terms could be dumped into a single string
    # if compiled it may be faster to run 
    
    # Another option would be to multithread based on forbidden terms as that's the smaller enitity
    # It could run async until the join to make the decision to keep/block the tweet 

    # EKL
    # Iterate through each tweet's terms and skip the tweet if one of the terms block it.
    # Not the most efficient way to do things.  Runtime is #tweets * #forbidden_words
    forbidden_terms = get_terms_list()
    cleaned_rows = []
    blocked_flag = False
    for row in rows:
      for word in forbidden_terms:
        # Need to check with the boundaries so we don't pick up "little" while filtering "lit"
        if re.search(r"\b"+word+r"\b",row[0]):
            # log it
            app.logger.warning("Blocked: ")
            app.logger.warning(row[0])
            # set blocked flag and abandon this tweet
            blocked_flag = True
            break
      if not blocked_flag:  
          cleaned_rows.append(row)
      else:
        #reset the flag
        blocked_flag = False

    # EKL
    # NOTE:  as the # of tweets increases this should be converted to a generator 
    # so it doesn't run into memory constraints

    return [{"tweet": row[0], "username": row[1]} for row in cleaned_rows]

@app.route("/tweets", methods=["GET", "POST"])
def tweets():
    if request.method == "POST":
        # EKL rejection of inappropriate tweets is handled in create_tweet
        # implementation could be changed to return error code but not sure
        # of requirements for this

        # If wanted to return http error code it would be something like
        # the following combined with a create_tweet return change 

        # NOTE: this theoretcal tidbit is not tested...
        
        # tweet = create_tweet(request.get_json())
        # if tweet != error_code:
        #    return (jsonify(tweet),201)
        # elif tweet == -1:
        #    return ('bad request', 400)


        tweet = create_tweet(request.get_json())
        return (jsonify(tweet), 201)

    # EKL  get_tweets should only return "clean" tweets
    return jsonify(get_tweets())


# Term API/functionality below ------------------------------------------------


def add_term(term):
    """
  Add a new term to the DB and return it as a dict.
  """
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute("INSERT INTO terms VALUES (?)", [term])
    conn.commit()
    conn.close()
    return {"term": term}


def delete_term(term):
    """
  Remove a term from the DB.
  """
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute("DELETE FROM terms WHERE term=(?)", [term])
    conn.commit()
    conn.close()


def get_terms():
    """
  Get a list of terms from the DB and return each as a dict.
  """
    #EKL  WHY?!?  Would be much easier as a list
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute("SELECT * FROM terms")
    ret = c.fetchall()
    conn.commit()
    conn.close()
    return [{"term": t[0]} for t in ret]

# EKL no sense in complaining about it...new function and leave the old 
# in case there's a dependency
def get_terms_list():
    """
  Get a list of terms from the DB and return each as a dict.
  """
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute("SELECT * FROM terms")
    ret = c.fetchall()
    conn.commit()
    conn.close()
    return [(t[0]) for t in ret]


@app.route("/terms", methods=["GET", "POST"])
def terms():
    if request.method == "POST":
        # TODO: mention that this gives errors sometime? Or not.
        json = request.get_json()
        # EKL  force the newly added term to lower case
        # Could return error if term includes punctuation as we 
        # ignore it during our match process
        # Does this need to be guarded against other unicode chars?
        # '; DROP TABLE terms; --   didn't do anything so that's a plus
        term = add_term(json["term"].lower())
        return (jsonify(term), 201)
    return jsonify(get_terms())


@app.route("/terms/<term>", methods=["DELETE"])
def term(term):
    delete_term(term)
    return ("", 204)


# Bootstrap/other setup -------------------------------------------------------


def bootstrap_db():
    """
  Create a fresh database with a few sample terms and a lot of tweets.
  """
    if os.path.exists(DBNAME):
        os.remove(DBNAME)
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    # create term table
    c.execute("CREATE TABLE terms (term text UNIQUE)")
    for term in ["bae", "fam", "totes", "lol", "lit"]:
        add_term(term)
    conn.commit()

    # create tweet table and load from JSON
    c.execute("CREATE TABLE tweets (tweet text, username text)")
    with open("tweets.json", "r") as f:
        for tweet in json.load(f):
            create_tweet(tweet, lenient=True)
    conn.commit()

    conn.close()


@app.route("/")
def ui():
    return render_template("index.html")


if __name__ == "__main__":
    bootstrap_db()
    app.run(host="0.0.0.0")
