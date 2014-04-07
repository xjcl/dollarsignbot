"""Partially based on Groompbot by /u/AndrewNeo
   
   Not really copied but come on how should I
   can't start with an empty page or whatever."""

import sys
import logging
import json
import praw
import time



def getReddit(settings):
    """Get a reference to Reddit."""
    r = praw.Reddit(user_agent=settings["reddit_ua"])
    try:
        r.login(settings["reddit_username"], settings["reddit_password"])
    except:
        logging.exception("Error logging into Reddit.")
        sys.exit(1)
    return r



def parse_comment(comment):
    """Respons to XXXX$ atm. Might be refined to only
       accept 'actual' values (7$, 7.50$, '7,50$') etc.
       or include corrections ('7$'->'$7')"""
    s = comment.body
    a = comment.body.split(" ")
    for e in a:
        if len(e)>1: # exclude singular "$"s
            if (
            ((e[-1] == "$") or (e[-2:] == "$."))
            and ("$$" not in e) and ("@" not in e)
            ):
            # "$$": 'they are in for the $$$' etc.
            # "@": I don't want to upset the linux community
            # 'xjcl@awesomeOS:~$ echo i am stupid'
                try:
                    logging.info("Responding to '"+e+"' ("+comment.id+")")
                    comment.reply("    beep boop, I am a robot, beep boop. "+
                    "The dollar sign goes in front of the number. beep boop.")
                    return comment.id
                except:
                    logging.info("Comment failed. "+
                    "/r/FreeKarma?")
                    logging.info("Unexpected error:", sys.exc_info()[0])
    return None


    
def listen(reddit, answered_coms, subreddits=["all"], limit=10000):
    subreddit = "+".join(subreddits)
    logging.info("Searching through these subreddits: "+subreddit)
    for comment in reddit.get_subreddit(subreddit).get_comments(limit=limit):
        #logging.info(comment)
        if comment.id not in answered_coms:
            new_id = parse_comment(comment)
            if new_id:
                print new_id
                answered_coms.append(new_id)
    return answered_coms




def loadSettings():
    """Load settings from file."""
    try:
        settingsFile = open("settings.json", "r")
    except IOError:
        logging.exception("Error opening settings.json.")
        sys.exit(1)
    settingStr = settingsFile.read()
    settingsFile.close()
    try:
        settings = json.loads(settingStr)
    except ValueError:
        logging.exception("Error parsing settings.json.")
        sys.exit(1)
    
    # Check integrity
    if (len(settings["reddit_username"]) == 0):
        logging.critical("Reddit username not set.")
        sys.exit(1)
    if (len(settings["reddit_password"]) == 0):
        logging.critical("Reddit password not set.")
        sys.exit(1)
    if (len(settings["reddit_ua"]) == 0):
        logging.critical("Reddit bot user agent not set.")
        sys.exit(1)
    #settings["parsing_option"] = str(settings["parsing_option"])
    return settings



def runBot():
    """Start a run of the bot."""
    logging.info("Starting bot.")
    settings = loadSettings()

    # Get reddit stuff
    logging.info("Logging into Reddit.")
    reddit = getReddit(settings)
    
    # Search comments and post
    # answered_coms prevents responding to the
    # same comment twice
    answered_coms = []
    try:
        of = open('answered_coms.txt', 'r')
        answered_coms = json.load(of)
        of.close()
    except IOError:
        logging.info("answered_coms.txt doesn't exits. Using empty list instead.")
        
    while True:
        logging.info("Looking for new comments.")
        answered_coms = listen(reddit, answered_coms, settings["subreddits"], 1000)
        logging.info("Writing comment ids to file.")
        sf = open('answered_coms.txt', 'w')
        json.dump(answered_coms, sf)
        sf.close()
        logging.info("Done!")
        time.sleep(20)



if __name__ == "__main__":
    # print to console - lots of errors while printing messages!?
    #logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    # print to log file
    logging.basicConfig(filename='log.log',level=logging.INFO)
    try:
        runBot()
    except SystemExit:
        logging.info("Exit called.")
    except:
        logging.exception("Uncaught exception.")
    logging.shutdown()
    
    
"""
"funny", "pics", "AskReddit", "IAmA", "AdviceAnimals", "WTF", "gifs", "gaming",
                     "teenagers", "explainlikeimfive", "videos", "todayilearned", "science", "Music",
                     "movies", "bestof", "books", "earthporn", "askscience", "mildlyinteresting",
                     "lifeprotips", "woahdude", "showerthoughts", "trees", "TrollXChromosomes",
                     "atheism", "tumblr", "GetMotivated", "thatHappened", "oddlysatisfying", "guns",
                     "worldnews", "bottest", "requestabot"])
"""
