from datetime import datetime
from time import sleep

from apscheduler.schedulers.blocking import BlockingScheduler

import config
from main import INSTA
from db import TimeLog, update_row
from aws_utility import upload, check_bucket

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=3)
def timed_job():
    username = config.username
    password = config.password

    # Generate Instagram_DataService object with above username and password
    insta = INSTA(username, password)

    following_ids = insta.get_followings()

    for username, id in following_ids.items():
        print ("username: %s" %username)
        try:
            story_response = insta.client.user_story_feed(id)
        except:
            sleep(10)

        if not story_response['reel']:
            continue
        try:
            preview_last_at = TimeLog.query.filter_by(username=username).first().last_at
        except:
            preview_last_at = 0
        print ("preview_last_at: %s" %preview_last_at)

        items = story_response['reel']['items']
        items = [item for item in items if item['taken_at'] > preview_last_at]
        if not items:
            continue

        character = story_response['reel']['user']['profile_pic_url']
        for item in items:
            taken_at = item['taken_at']

            if 'image_versions2' in item.keys():
                image_url = item['image_versions2']['candidates'][0]['url']
                image_name = username + "_" + datetime.fromtimestamp(taken_at).strftime('%m%d%Y%H') + ".jpeg"
                image_name = upload(image_url, image_name)
            else:
                image_name = ""

            if 'video_versions' in item.keys():
                video_url = item['video_versions'][0]['url']
                video_name = username + "_" + datetime.fromtimestamp(taken_at).strftime('%m%d%Y%H') + ".mp4"
                video_name = upload(video_url, video_name)
            else:
                video_name = ""

            taken_at = datetime.fromtimestamp(taken_at).strftime('%m/%d/%Y %H:%M:%S')

            # if image_name:
            #     logo = detect_logos_uri(image_name)
            #     text = detect_text_uri(image_name)
            # else:
            #     logo = ""
            #     text = ""

            # save_story(username, character, image_name, video_name, taken_at, logo, text)
            print("taken_at: %s" %taken_at)

        last_at = items[-1]['taken_at']
        update_row(username, last_at)

        print ("userEnd")

if __name__ == "__main__":
    check_bucket(config.aws_bucket)
    sched.start()