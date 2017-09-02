import codecs
import json
import os
from time import sleep
import random

import config

logger = config.logger

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(config.ROOTPATH)
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        logger.info('SAVED: {0!s}'.format(new_settings_file))


def getAttribute(obj):
    output = {}
    for key, value in obj.__dict__.items():
        if type(value) is list:
            output[key] = [getAttribute(item) for item in value]
        else:
            try:
                output[key] = getAttribute(value)
            except:
                output[key] = value

    return output


class INSTA():
    '''Main class of the project'''
    def __init__(self, username, password):
        '''
        :param username: Instagram Login Username
        :param password: Instagram Login Password
        '''
        device_id = None
        try:
            settings_file = config.settings_file_path
            if not os.path.isfile(settings_file):
                # settings file does not exist
                logger.info('Unable to find file: {0!s}'.format(config.settings_file_path))

                # login new
                self.client = Client(
                    username, password,
                    on_login=lambda x: onlogin_callback(x, config.settings_file_path))
            else:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=from_json)
                logger.info('Reusing settings: {0!s}'.format(settings_file))

                device_id = cached_settings.get('device_id')
                # reuse auth settings
                self.client = Client(
                    username, password,
                    settings=cached_settings)

        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            logger.info('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

            # Login expired
            # Do relogin but use default ua, keys and such
            self.client = Client(
                username, password,
                device_id=device_id,
                on_login=lambda x: onlogin_callback(x, config.settings_file_path))

        except ClientLoginError as e:
            logger.info('ClientLoginError {0!s}'.format(e))
            exit(9)
        except ClientError as e:
            logger.info('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
            exit(9)
        except Exception as e:
            logger.info('Unexpected Exception: {0!s}'.format(e))
            exit(99)

        self.user_id = self.client.username_info(username)['user']['pk']

    def get_userId(self, username):
        return self.client.username_info(username)['user']['pk']

def get_lines(txtFile):
    try:
        with open(txtFile) as f:
            lines = f.readlines()
            return [line.strip() for line in lines]
    except:
        print ('%s does not exist' %txtFile)

def list2txt(path, data):
    data = "\n".join(data)
    with open(path, 'w') as f:
        f.write(data)


def main():
    # username = "cristiano"
    # user_id = insta.get_userId(username)
    # insta.client.friendships_create(user_id)
    count = 1
    while (len(userList)) > 0:
        username = userList[0]
        while True:
            try:
                user_id = insta.get_userId(username)
                insta.client.friendships_create(user_id)
                userList.remove(username)
                list2txt(filepath, userList)
                sleep(random.randint(30, 48))
                count += 1
                logger.info(username)
                logger.info(count)
                print (username)
                print (count)
                break
            except ClientError as e:
                logger.error(e)
                print(e)
                if e.msg == "Not Found: User not found":
                    userList.remove(username)
                    list2txt(filepath, userList)
                    break
                else:
                    sleep(100)
            except Exception as e:
                logger.error(e)
                print ('Exceotion')
                sleep(100)

    # print (insta_client.user_id)


if __name__ == "__main__":
    filepath = "users.txt"
    # userList = list(set(get_lines('users.txt')))
    userList = get_lines(filepath)
    print (userList)
    print (len(userList))

    # userList.remove('cristiano')
    # list2txt(filepath, userList)
    # userList = get_lines(filepath)
    # print(userList)
    # print(len(userList))

    insta_username = config.username
    insta_password = config.password
    insta = INSTA(insta_username, insta_password)

    main()

    # r = insta.client.feed_tag('momblogger')
    # print (r)









