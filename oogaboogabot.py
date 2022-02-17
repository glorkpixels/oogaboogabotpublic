import tweepy
import json
import requests
import os
import logging
import credentials
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def globul():
    global img 
    img= Image.open("oogaboogaaa.jpg")
    global draw 
    draw = ImageDraw.Draw(img)
    global font 
    font = ImageFont.truetype("impact.ttf", 30)

globul()
consumer_key = credentials.API_key
consumer_secret_key = credentials.API_secret_key
access_token = credentials.access_token
access_token_secret = credentials.access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# For adding logs in application
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

def drawTextWithOutline(text, x, y):
    draw.text((x-2, y-2), text,(0,0,0),font=font)
    draw.text((x+2, y-2), text,(0,0,0),font=font)
    draw.text((x+2, y+2), text,(0,0,0),font=font)
    draw.text((x-2, y+2), text,(0,0,0),font=font)
    draw.text((x, y), text, (255,255,255), font=font)
    


def drawText(text, pos):
    text = text.upper()
    w, h = draw.textsize(text, font) # measure the size the text will take

    lineCount = 1
    if w > img.width:
        lineCount = int(round((w / img.width) + 1))

    lines = []
    if lineCount > 1:

        lastCut = 0
        isLast = False
        for i in range(0,lineCount):
            if lastCut == 0:
                cut = (len(text) / lineCount) * i
            else:
                cut = lastCut

            if i < lineCount-1:
                nextCut = (len(text) / lineCount) * (i+1)
            else:
                nextCut = len(text)
                isLast = True

            print("cut: {} -> {}".format(cut, nextCut))

            # make sure we don't cut words in half
            if nextCut == len(text) or text[int(nextCut)] == " ":
                print("may cut")
            else:
                while text[int(nextCut)] != " ":
                    nextCut += 1

            line = text[int(cut):int(nextCut)].strip()

            # is line still fitting ?
            w, h = draw.textsize(line, font)
            if not isLast and w > img.width:
              
                nextCut -= 1
                while text[nextCut] != " ":
                    nextCut -= 1
               
            lastCut = nextCut
            lines.append(text[int(cut):int(nextCut)].strip())

    else:
        lines.append(text)
    lastY = -h
    if pos == "bottom":
        lastY = img.height - h * (lineCount+1) - 10

    for i in range(0, lineCount):
        w, h = draw.textsize(lines[i], font)
        x = img.width/2 - w/2
        y = lastY + h
        if pos == "top":
            drawTextWithOutline(lines[i].upper(), x, y)
        if pos == "bottom":
            drawTextWithOutline(lines[i].lower(), x, y)
        lastY = y
    

def get_last_tweet(file):
    f = open(file, 'r')
    lastId = int(f.read().strip())
    f.close()
    return lastId

def put_last_tweet(file, Id):
    f = open(file, 'w')
    f.write(str(Id))
    f.close()
    logger.info("Updated the file with the latest tweet Id")
    

def respondToTweet(file='tweet_ID.txt'):
    
    last_id = get_last_tweet(file)
    mentions = api.mentions_timeline(last_id, tweet_mode='extended')
    if len(mentions) == 0:
        return

    new_id = 0
    logger.info("someone mentioned me...")

    for mention in reversed(mentions):
        logger.info(str(mention.id) + '-' + mention.full_text)
        new_id = mention.id
        if '#oogaboogait' in mention.full_text.lower():
            if mention.in_reply_to_status_id is not None:
                tweetFetched = api.get_status(mention.in_reply_to_status_id)
                replytw = tweetFetched.text
                replytw = ' '.join(word for word in replytw.split(' ') if not word.startswith('@'))
            
                logger.info("Responding back with oogaboogait to -{}".format(mention.id))
                try:
                    tweet = replytw
                    drawText(replytw, "top")
                    drawText("[OOGA BOOGA NOISES]", "bottom")
                    img.save("created_image.jpg")
                    media = api.media_upload("created_image.jpg")
                    
                    logger.info("liking and replying to tweet")

                    api.create_favorite(mention.id)
                    api.update_status('@' + mention.user.screen_name + " Ooga Booga", mention.id,
                                    media_ids=[media.media_id])
                    
                    put_last_tweet(file, new_id)
                    os.remove("created_image.jpg")
                except:
                    logger.info("Already replied to {}".format(mention.id))
        elif '#likeme' in mention.full_text.lower():
            try:
                tweetFetched = api.get_status(mention.in_reply_to_status_id)
                logger.info("Responding back to self centered piece of shit -{}".format(mention.id))
                    
                logger.info("liking and replying to tweet")

                api.create_favorite(mention.id)
                api.update_status('@' + mention.user.screen_name + " Okey, you self-centered shit.", mention.id)
            except:
                logger.info("Already replied to {}".format(mention.id))
        globul()

        

            


if __name__=="__main__":
    respondToTweet()