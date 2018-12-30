# Dash On Heroku

![page](dash-heroku.gif)

## Description
Web application written in Python using Dash framework and deployed on a Heroku dyno
(Heroku containers are called Dynos)

## What is it doing?
It's a single page webapp with two graphs:
1. CPU (combined) and Virtual Memory consumed on the Heroku Dyno in real time
2. Bytes sent/recv in real time

## Motivation
For fun, and to get familiar with Dash and Heroku deployments.


## Instructions to clone/deploy this app on Heroku

### 1. Install Heroku CLI
#### Mac
    brew install heroku/brew/heroku
#### Ubuntu 16+
    sudo snap install --classic heroku
#### Windows
get installer from:
https://devcenter.heroku.com/articles/heroku-cli

### 2. create/login to your heroku account
    heroku login

### 3. Clone the repo
    heroku git:clone -a dash-on-heroku
    cd dash-on-heroku

### 4. Deploy
    git add .
    git commit -am "dash-on-heroku clone"
    git push heroku master

