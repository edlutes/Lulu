# Lulu Code Challenge

## Scenario

You're an entrepreneur looking to explore the social media market. You decide to make a mirror of Twitter that filters out tweets that certain audiences might not want to hear:

* `apoliticaltwitter.com`, for tired citizens avoiding political tweets
* `gotlesstwitter.com`, for Game of Thrones fans wanting to avoid discussions/spoilers
* `curmudgeontwitter.com`, for those who don't want any of that new-fangled talk like "bae" or "lol"

The API for these mirrors can be deployed to multiple domains. Each instance can be configured with certain terms, and tweets containing those terms will be omitted when listing tweets. Users can also create tweets, so long as they don't contain any of the terms that mirror is supposed to avoid, because that would just be hypocritical.

## Setup

Enclosed you'll find a small Flask app and code for a tiny UI. This code is paired with a Dockerfile, so as long as you have Docker installed, you should be able to run the app like so from within the `lulu-code-challenge` directory.

```
docker build -t tweet-mirror . && docker run -p 5000:5000 --rm tweet-mirror
```

If that's successful, the UI should be available at [localhost:5000](http://localhost:5000).

## Your Task

Your job is to complete the backend code provided (see `server.py`) so that:

* Complete the `get_terms_from_tweet` function so that it's smarter about parsing tweets into terms.
* Make the `GET /tweets` endpoint exclude results that contain 1+ of the terms to avoid.
* Make the `POST /tweets` endpoint reject new tweets that include 1+ of the terms to avoid.
* Additionally:
  * fix and document any errors you run into
  * document any inefficiencies you find, or things you'd do differently

When you're done, you can submit your finished code as well as any documentation via ZIP attachment to email, GitHub, etc.
