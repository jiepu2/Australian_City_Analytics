import couchdb
import json
import queue
import sys
import time
import tweepy
from tweepy import OAuthHandler

#args = sys.argv

#for arg in args:
#    print(arg)
couchIP = 'sourcead:iamfine@115.146.93.79' # IP of master couchdb
#couchIP = 'localhost'
threadRank = 1
threadCount = 4 #int(args[2])
databaseName = 'twitter'
databaseNameSource = 'source'
nameSourceID = 'sourcelist'

accounts = [] # for fetching status
accountPos = 0 # current account fetching
unfetchedUserQueueCapacity = 100
peopleMaxCount = 25000 # Max amount of people fetching
statusMaxCount = 200 # Max amount of statuses of one person
friendMaxCount = 20 # Max amount of friends of one person to be added to queue
couch = couchdb.Server('http://' + couchIP + ':5984')
db = None

databasetime = 0 # for timing
tweettime = 0

#isMaster = True

# to judge master
#try:
#    couchVarify = couchdb.Server('http://127.0.0.1:5984')
#    couchVarify['_users']
#except ConnectionRefusedError:
#    isMaster = False

#if isMaster:
# to create or get db of all statuses
try:
    db = couch[databaseName]
except couchdb.http.ResourceNotFound:
    try:
        db = couch.create(databaseName)
    except couchdb.http.PreconditionFailed:
        pass

# fetchedUser = {}
unfetchedUser = queue.Queue(maxsize = unfetchedUserQueueCapacity)

# account setting
# yingchuang
accounts.append({
'consumer_key' : '4eEm0v4afh2MH9juRASmR3xd0',
'consumer_secret' : 'ek5x4au3LBo25iBcwKf9lzJMViz1KCoYApbPIYstHZgWJHHFHY',
'access_token' : '853442542074908672-A3pnyKH3xVGC65s5lvtZnIPMymGL4kb',
'access_secret' : 'UgORHfIhuvCYAH11nwejwupfN92Lu9GKpyBbSc6HAOttT'})

accounts.append({
'consumer_key' : 'Ahm52ivjZ9aLxdF8mGGhhKhKU',
'consumer_secret' : 'eyGbe8yBHendsSOxyoZ99Z0ohMl1NDuJtUG3rL39Ic3V50hkFF',
'access_token' : '853442542074908672-7t6ztvCOsHqClazlbxFKe2p1YTFIfAB',
'access_secret' : '50FpJK7S5Cdabmm6kQr0ikWWe3FY83y3sRZrB8tX265XO'})

accounts.append({
'consumer_key' : '0QblwtahftHzpUY6JNBKJlYxH',
'consumer_secret' : 'mC7ZnBBKSNipAlmwQ2johuhugx0m3wZCnO2yChjZxxkLn7oDUQ',
'access_token' : '853442542074908672-glcGvuSrkTZmkoppCnbjd9ULLFjourF',
'access_secret' : 'JheGGn1NTR2JwDNVc2lKW64cNfsGOOvAqJ63aU458SVBk'})

accounts.append({
'consumer_key' : 'xe9mVovHE49pll0BedCxckxoj',
'consumer_secret' : 'Buy7Y5eBjbypLveoqEXEj9exCpDspWUCI9hag9Z8Iigd7YAsOJ',
'access_token' : '853442542074908672-BOEyHjWAQFu2IuvJKOGy22qdK32o4Q1',
'access_secret' : 'rufPkPAeJXf1p1xuCSowZGspLFU0AMoQ45q4CyjXWz6PF'})

accounts.append({
'consumer_key' : 'NhmAGuRvOhen2EXoReEvFPhn9',
'consumer_secret' : 'q2ZrUQrdInVAHKr2ClVBqv3RfCIB2jO4A2HLm5QifwYmIcoXEu',
'access_token' : '853442542074908672-nAf6QrTJjHasdmXqtghe7FoIz54dRCk',
'access_secret' : 'DGckFXikMtxjmGM16pGCp2pgXGvz7O6hDw0Fe7fRzglXA'})

# arthur
accounts.append({
'consumer_key' : '7NW9RyZLWnXE7jbbgC7Q5ErJw',
'consumer_secret' : 'Vmkp7ZrAVTVob0Cxr2lGMFokjNKvKLTWQtrVbWmf8FaP9E48Jx',
'access_token' : '4444601909-kdjeiUNVq4eIFpkXUGuRPJUAoQImceVIcPzBAgK',
'access_secret' : 'A7lOd2DZ38SnpUcXNQvd8QT7m16B0Ckm8xuyw55qFrIO9'})

accounts.append({
'consumer_key' : 'e4Fv8KAwQ5L5A5NZxqMANJuuz',
'consumer_secret' : 'b3kQg69dKxVcpYMaeaSvkQSaWxLZoFsIp4cQnzU033daWCAUgt',
'access_token' : '854235761587048449-467HV6EMSqsuHbSmrvRICZHoMPuTJUT',
'access_secret' : 'UzX374xOJJBD10Rzm5nBqXw949f4eGUDEt6V7fKRbGdpZ'})

accounts.append({
'consumer_key' : 'dQtpEQrxmlfRiQczGwG8nXMbp',
'consumer_secret' : 'RGNlbrkPRzFA9XQB3tCKtDbUeAh3tGOTkdXKq17pjTzXjVEqDa',
'access_token' : '4444601909-rEsfeP8bDq7aKWyeJP4GWuk3HiQXwCdzKudLG3s',
'access_secret' : 'QPYnCZejVtbPP3bGBibNZzeaOOSsXloiIeP2Qo4DKOJWH'})

accounts.append({
'consumer_key' : 'bcypBvJdToHd3tN1LieuDfPJu',
'consumer_secret' : 'rogOKksgJU46NeXB5Cdmy40TJBZyVZkVtFxkkTZyXPBosvkjSd',
'access_token' : '4444601909-peSS6eUsgXxNUDdZxm1HQ0Reg9OnqQyqiGIazhV',
'access_secret' : '4KNmPFXSO0tM10FFDiRmJ0ZXecRGND2hKuROd0A25ba4K'})

accounts.append({
'consumer_key' : '7xdxfkr5gEKSsmF0DX6hRYL16',
'consumer_secret' : 'Gxrl8LH8bgKhroexnYQvpD4ZqHJhBT6TZHIDaj9H4jViz4vwIi',
'access_token' : '4444601909-0VwZQd6nFZuPpbThO71EwHm9eHSmnlH0RvLLksg',
'access_secret' : 'NtHCGjj7AXJDSPEfIZsYrtjvByCf7ogvpm9zqNUbaZbJL'})

accounts.append({
'consumer_key' : '7NW9RyZLWnXE7jbbgC7Q5ErJw',
'consumer_secret' : 'Vmkp7ZrAVTVob0Cxr2lGMFokjNKvKLTWQtrVbWmf8FaP9E48Jx',
'access_token' : '4444601909-kdjeiUNVq4eIFpkXUGuRPJUAoQImceVIcPzBAgK',
'access_secret' : 'A7lOd2DZ38SnpUcXNQvd8QT7m16B0Ckm8xuyw55qFrIO9'})

accounts.append({
'consumer_key' : 'rEC4hwWzesBL4RWbFzxrhFakG',
'consumer_secret' : 'nXCP3qKW9D1DmHjqvk4hovDXA5oyH6uy7yP3M24LmbgWKb50dv',
'access_token' : '4444601909-wx1dYmwFIUUN5Z0ti2IyglyZZNocgOfPXKnNG7W',
'access_secret' : 'aCjI2ExAC0FggfgzI6BtsjAz3zL0M8edHC8piOsjGxC5P'})

accounts.append({
'consumer_key' : 'V51Fzvh89TNDwNmnkHUOLuoYg',
'consumer_secret' : 'zkQ0UrSsox0sfWJStdUH763HYzLufg73YpHX28ZwrOLoxpVwVc',
'access_token' : '4444601909-Cconi2L2ZTkI0h1LO6D3czBZtVGdLqgHV6Ofjm9',
'access_secret' : 'dLGpzyYVWkYHxj7Dt5OCtxsiHwQpEVK1wZB8o1SmG6V3t'})

accounts.append({
'consumer_key' : 'ozCn4SrkepajOW6AIL06PvjGs',
'consumer_secret' : 'CeC0Jj7axyOStyoruT6cyR1HidIc4NQRKeWeecgDZuTbF1KM3E',
'access_token' : '4444601909-nM7OCTy2lprrlQvh9OeHY6YVQjXxfoIFBkBsFcb',
'access_secret' : 'batdpIYlIAYhyiAUjUF35BMT9QcdlR6lzmG5fYPIuJJBX'})

# kwei
accounts.append({
'consumer_key' : 'B8PeDuAVGycIPn73ceE0vLo1e',
'consumer_secret' : 'daF1UjcwavAnoFiHnNxAmyuJevG2JU9GlEYoTkRLsWiKqWb6fY',
'access_token' : '2575592904-JWrYORjYN0JPX85Q2Cbo5lYTjOpNfiNiT3fQ6Dq',
'access_secret' : '6eaZYdPSXIDA9Sr9TEvTFp0OR4aCFlDjupKPxb99TSAeY'})

accounts.append({
'consumer_key' : '48YW6WZRjyPtMGwR6VX7lBieE',
'consumer_secret' : 'wVes0R25aoNEiLcdfwTlPngZCFaF4AE7eeQpWflZtbJpo3k3eA',
'access_token' : '854237152212688896-CsaNyvQ0eIkfrDuz5TOZVCzdFpv6Peo',
'access_secret' : '6BhuokvlK1LvRH7BLCS7ZkPG2lql5TPV8SXojfeVkRc0i'})

accounts.append({
'consumer_key' : 'BISq0gnPO5sKPmSGIDDX8CoNi',
'consumer_secret' : 'wqwZPU7Eq1YBxSTGagFoy5OHcuYyoJ7cs6Wrg7yz0C8gvki6kU',
'access_token' : '854237152212688896-sjbpQYfsArfzvCKTmSqxjt5d5Lj4Ui4',
'access_secret' : '7AP93iXzTNPlJdtccQLkCb047SPXdJhJ2mIr3gwR0KkUK'})

accounts.append({
'consumer_key' : '0hDkVWYVtI3FbPBO0eabByMJr',
'consumer_secret' : 'IM4IBDHosLw1GrG5rX0pVQy9vv3wxwZdGS630lD7YPpVCZ21n2',
'access_token' : '854237152212688896-lGvQMrSPKA3I8daYWR4q20TCNi5oEah',
'access_secret' : 'UwJ2GjZjAlJmcuHhSk32WPo35RTTk8DCqhG7A3jiudUqj'})

accounts.append({
'consumer_key' : 'ZMcJlgB2POlzVbqQVgwBfMes5',
'consumer_secret' : 'tL3Ch94uEORN7dZrrWEoKZdjVPiMYscE0Am5a1MqUyskFmXTwD',
'access_token' : '2575592904-DFVFcTEZ7bB4qVCAanC32jiGJtU5LP02eOuESFK',
'access_secret' : '0HsSuWz3MpKMqWYxSod77WVW5WXX10Trq13z5Nry348bN'})

accounts.append({
'consumer_key' : '2c56wTHKAS21gA4UAZzkkwzqZ',
'consumer_secret' : 'fxAfJHIBqHGwL0f42zlzUEtJUmsxyHAD8MQ7gEqYqaau7KZyxJ',
'access_token' : '2575592904-mQN46mJwpSMj9CW5jakd79c5T34x7DjBApSf4W5',
'access_secret' : 'bYFLbECe6EjNvKM6xm4BEzA6IZk00HZ5XtaFwJ4GxfhGp'})

accounts.append({
'consumer_key' : 'QVpJC7lLXt0VqSRiB4oWOxLux',
'consumer_secret' : 'r0rQgZku1qtZtdXV1z4luOh2yiWNPWGxhdfxhl0RPyqkASCJxc',
'access_token' : '2575592904-rjouP5t0EJ1iu7vFM3kU5DBKLAZHA94YzSvtau6',
'access_secret' : 'gql0ekQiHWx5rQmurJKFp9EiNrvl6MJ7mF04rqFBwGGYx'})

# amyxie1994
accounts.append({
'consumer_key' : 'gbqEmrklOoqFEpvEFfYFmufqF',
'consumer_secret' : 'QgzOCavAiPh1wWrSAPBvj7ZZQyMJ9KxUp4Qz8SSh1WzgblQ7oE',
'access_token' : '853486226443194368-M6NEQ1DGRZX8eUUKmaXj9CsY3vv7gLA',
'access_secret' : '8qxOum5J3Uuc4kbpnoNykBoDQcHSzTF4xW9JRWhZwIbdh'})

# nanjiangl
accounts.append({
'consumer_key' : 'pXWJNLIVTT8NNmO5X2x7nQf2P',
'consumer_secret' : 'RETU3DeIbqq111XWBByJppmOOZHDNnMsb4ergE2ZQZlUDVeFCY',
'access_token' : '851662491927040000-df4TR9seEcvDWGva4OcNjMrPAC0z0ik',
'access_secret' : '0zCj63JPIcx28g1UcquZKv3vnTGXHJFaO60sPgOQgbmHY'})

accounts.append({
'consumer_key' : 'oqUpEOmJwT63m2ifD45EwWgOJ',
'consumer_secret' : 'Qd3hcSkzAATYZQpv9z5AjvOkOIqdN6fvOU1JNlGB1BsgJ0j3zp',
'access_token' : '851662491927040000-7gLy5OGe00h8evy5jKKBSNOanAVZeFn',
'access_secret' : 'd5BjxJ5EnYZG02bBpPmwpB2fF7ZuWoUzH96xmhoVef6JX'})

accounts.append({
'consumer_key' : 'D1CUDFJ8aLZ9D8VGy6vcleYfP',
'consumer_secret' : '12TndZwTsN5YReB2YJx0xIPmSvUlr7HbdBbWasrqZwA8Bks76z',
'access_token' : '851662491927040000-RLTayq8a5pzT0zz337skagbe36osxbd',
'access_secret' : 'eZ2pcRvumBQ5eO9E96VFM3XLLacf0dVwJEeBrJdSpLykR'})

accounts.append({
'consumer_key' : 'Z54Zw9U1v5HwE63UJgio1C2Eh',
'consumer_secret' : 'HebEb4OereuW3VKTSByShOIV10N8hgadyrMXc3KSywJDoCGv1V',
'access_token' : '851662491927040000-VNCzPjxMMU3wSxEC1CbshQJVkh1ie8Q',
'access_secret' : 'hmtQPook0vBXQzzpgmaAvcWqzyRtXQhctaVgk61YBboIP'})

accounts.append({
'consumer_key' : 'g5pLp0KLQ5hgRcR3fxTxQsd5p',
'consumer_secret' : 'RtgxcATM7I5ELmEnLycjI1JUBI6GY7BQF6xP2BIPY5YkvfSU40',
'access_token' : '854862643948957696-iRKez7j7mjH32YNqiKi36eotm2U2qEv',
'access_secret' : 'cGdFdOwrVHOKP37GGzqaD6SuElsb7D7Fa1nXYkGpH9DcK'})

accounts.append({
'consumer_key' : 'ybqdx2QUlaXGfuPtvq5xDum5s',
'consumer_secret' : 'XCmegsIkx5DhFEsfdukpwVLTcvCeObG6PVx073pYGFAiN5tvwd',
'access_token' : '854862643948957696-sJezdcXBvXLTqBM3V7ltJ7EX99v76Ve',
'access_secret' : 'ATo8pboqahtHE3AnGqeDd9bOGLoXtiQEcjpAawdORB4AV'})

accounts.append({
'consumer_key' : 'RbMGm2WJE1P7eQQJkYJwO8RuR',
'consumer_secret' : 'o2AwpUtXCM8mUDNmYTitCPBuqmXtkeWm7PANE1W2PN1Rmc0aaB',
'access_token' : '854862643948957696-N44ZODQraL0fpFFGCuP0wgDLKIcARCk',
'access_secret' : 'JfSi4XZ5fo0ZlxDfwuxs4cSDQnlaZQ0yS4VYOWEvHaFqc'})

accounts.append({
'consumer_key' : 'z0OFMGNhUeNyr3BLJUzP9nQ6t',
'consumer_secret' : 'D5rxzXStJZVo8UxNCu707lljqwjytsJTr4ZEIAEgYEZMcrU5Rh',
'access_token' : '854891237358186496-Ul8AHeMDRgyjrKXSdt4PD40Kkku693s',
'access_secret' : 'kWO9T8BZQBKMlrFUaXC2lDa8jD3f8dU7RNlXoxrpNoZ9Y'})

accounts.append({
'consumer_key' : '7rF55CFf3JWQNk5iEsBLIDqzM',
'consumer_secret' : 'EwdO46xaOrWXkh4raX0prEAWzBCHKOB2JDqhrALcvSrIFSJQRy',
'access_token' : '854891237358186496-7WkKebZtQbitwSHRw3nZYEoxjzgVE0O',
'access_secret' : 'nY9gniL3jUSv5YQUv5l4Sy8MS0Iufyj8UJqKkCoAjnNds'})

accounts.append({
'consumer_key' : 'ZppJmYBBlRz0H50G3UIk2cfy2',
'consumer_secret' : 'GX0rDbhcgsXb6qlvAnWIjLung3G8ELPfzdhrs4kU2EJiNMuX58',
'access_token' : '854891237358186496-ti1HW24Xk49vG2S8xvmES8oGvI8xBQR',
'access_secret' : 'A3f1AYO4vYOgfaSywTtGgksZybBhdtXA1QMbmB5DQfmvt'})

# add account to api
apis = []
for account in accounts:
    auth = OAuthHandler(account['consumer_key'], account['consumer_secret'])
    auth.set_access_token(account['access_token'], account['access_secret'])
    apis.append(tweepy.API(auth))
    #print(account)
print("accounts added")
# get start name
dbSource = couch[databaseNameSource]
print("dbSource")
try:
    while True:
        try:
            print('nameDoc')
            nameDoc = dbSource[nameSourceID]
            threadRank = nameDoc['count']
            startIndex = int(threadRank / threadCount * len(nameDoc['name']))
            endIndex = int((threadRank + 1) / threadCount * len(nameDoc['name']))
            for i in range(startIndex,endIndex):
                unfetchedUser.put(nameDoc['name'][i])
            # unfetchedUser.put(nameDoc['name'][0])
            nameDoc['count'] += 1
            a = dbSource.save(nameDoc)
            accountPos += int(threadRank * (len(accounts) / threadCount + 1))
            break
        except couchdb.http.ResourceConflict as e:
            print(e, sys._getframe().f_lineno)

    def city(str):
        citylist = ['Canberra','Sydney','Melbourne','Brisbane','Perth','Darwin','Adelaide','Hobart']
        for c in citylist:
            if c in str:
                return c
        return ''
    def location(friend):
        locationString = friend.location
        if locationString != '' and locationString is not None:
            local = city(locationString)
            if local != '':
                return local
        locationString = friend.time_zone
        if locationString != '' and locationString is not None:
            local = city(locationString)
            if local != '':
                return local
        try:
            locationString = friend.status.place
            if locationString != '' and locationString is not None:
                local = city(locationString.name)
                if local != '':
                    return local
        except Exception:
            pass
        return ''

    # start fetching
    starttime = time.time()
    for i in range(peopleMaxCount):
        screenName = unfetchedUser.get()
        print(screenName, unfetchedUser.qsize())

        # fetch friends
        while True:
            try:
                if unfetchedUserQueueCapacity - unfetchedUser.qsize() < 20:
                    break
                friendCount = min(unfetchedUserQueueCapacity - unfetchedUser.qsize(),friendMaxCount)
                for friend in tweepy.Cursor(apis[accountPos].friends, screen_name = screenName).items(friendCount):
                    # judge other conditions
                    if friend.lang != 'en' or friend.followers_count < 5 or friend.statuses_count < 10:
                        continue
                    local = location(friend)
                    if local == '':
                        continue
                    try:
                        db[friend.screen_name] # judge is existing
                        print(friend.screen_name, "re")
                    except couchdb.http.ResourceNotFound:
                        unfetchedUser.put(friend.screen_name)
                    except Exception as e:
                        print(e,sys._getframe().f_lineno)
                break
            except tweepy.error.RateLimitError as e:
                accountPos = accountPos + 1
                accountPos = accountPos % len(accounts)
                time.sleep(5)
                print(e,accountPos,'friend',sys._getframe().f_lineno)
            except tweepy.error.TweepError as e:
                if e.response is None:
                    raise e
                elif e.api_code == 326:
                    accountPos = accountPos + 1
                    accountPos = accountPos % len(accounts)
                    time.sleep(5)
                    print(e,accountPos,'friend e.api_code 326',sys._getframe().f_lineno)
                elif e.response.status_code in set([401, 404]): ##############
                    print(e,"status_code 401 404",sys._getframe().f_lineno)
                    break
                else:
                    print(e,'friend',sys._getframe().f_lineno)
                    break
        # fetch statuses
        while True:
            try:
                statusJsons = []
                statusCount = 0
                finished = False
                id = ''
                for status in tweepy.Cursor(apis[accountPos].user_timeline, screen_name = screenName, include_rts = False).items(statusMaxCount):
                    # statusJsons.append(status._json)
                    statusJsons.append({"time":status.created_at.hour,'location':location(status.user),'text':status.text,'coordinates':status._json['coordinates']})
                    id = status.id_str
                for status in tweepy.Cursor(apis[accountPos].user_timeline, screen_name = screenName, max_id =id, include_rts = False).items(statusMaxCount):
                    statusJsons.append({"time":status.created_at.hour,'text':status.text,'coordinates':status._json['coordinates']})
                if len(statusJsons) > 0:
                    if screenName[0] == '_': # delete underscore in 1st place of name
                        print(screenName)
                        screenName = screenName[1:-1]
                        print(screenName)
                    saveDict = {'_id':screenName,'status':statusJsons}
                    while True:
                        try:
                            db.save(saveDict)
                            break
                        except Exception as e:
                            print(e,sys._getframe().f_lineno)
                            break
                break
            except tweepy.error.RateLimitError as e:
                # error too many requests
                accountPos = accountPos + 1
                accountPos = accountPos % len(accounts)
                time.sleep(5)
                print(e,accountPos,'status',sys._getframe().f_lineno)
            except tweepy.error.TweepError as e:
                if e.response is None:
                    print(e,"None",sys._getframe().f_lineno)
                elif e.response.status_code in set([326,429]):
                #elif e.api_code == 326:
                    accountPos = accountPos + 1
                    accountPos = accountPos % len(accounts)
                    time.sleep(5)
                    print(e,sys._getframe().f_lineno)
                else:
                    print(e,sys._getframe().f_lineno)
                    break
        print(time.time() - starttime,i)
    while not unfetchedUser.empty():
        print(unfetchedUser.get())
except Exception as e:
    f=open('cluster.out','w',encoding='utf8')
    while not unfetchedUser.empty():
        str = unfetchedUser.get()
        f.write(str)
        print(str)
    print(e,sys._getframe().f_lineno)