# encoding=utf-8

#######################
#
# 第一次 2015-07-19 21:27:01 分，共计 7307 条
# 其中，有效 7172 条，135 条被微博删除
# 共计 498 个 tag；9655 条 post - tag 关系；
#
#######################

import time, json
import dbutils
from weibo import APIClient

_MIN_POST_ID = 0
_START = 90
_END = 189


def _create_client():
    secret = dbutils.getSecret()
    return APIClient(secret.app, secret.secret, 'http://marked.sinaapp.com/callback')


# Step 1.
def load_raw_posts(client):
    for i in range(_START, _END):
        print 'Iteration ${} is running ...'.format(i)
        favlist = client.favorites.get(count=50, page=i)
        dbutils.insertRawPosts(favlist.favorites)
        time.sleep(21)


# Step 2.
def uniq_raw_posts():
    posts = dbutils.getRawPosts()
    if not posts:
        posts = []

    ids = {}
    mintime = 2420485364
    maxtime = 0
    for post in posts:
        fav = json.loads(post.content)
        id = fav['status']['id']
        if int(id) <= _MIN_POST_ID:
            continue
        if id in ids:
            print "    - found dup id: {}".format(id)
            continue
        ids[id] = post.content
        favtime = time2timestamp(fav['favorited_time'])
        if favtime > maxtime:
            maxtime = favtime
        if favtime < mintime:
            mintime = favtime
    dbutils.insertUniqRawPosts(ids)
    print "post num: %d,  mintime: %s,  maxtime: %s" % (len(ids), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mintime)), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(maxtime)))


# step 3. 从 uniq_raw_posts 表中获取数据，然后整理后放到 favorites 表中
def parse_posts():
    posts = dbutils.getUniqRawPosts(['id > "%s"', _MIN_POST_ID])
    if not posts:
        posts = []

    favorites = []
    tags = {}
    posts_tags = {}
    deleted = 0
    for post in posts:
        if int(post.id) <= _MIN_POST_ID:
            continue

        fav_data = {'re_created_at':'0000-00-00 00:00:00', 're_post_text':'', 're_id':'', 're_pic_urls':'', 're_user_id':'', 're_profile_url':'', 're_profile_image_url':'', 're_screen_name':'', 're_url':''}

        fav = json.loads(post.content)
        # 处理微博被删的情况
        if fav['status'].has_key('deleted') and fav['status']['deleted'] == "1":
            deleted += 1
            continue

        fav_data['id'] = post.id
        favtime = time2timestamp(fav['favorited_time'])
        fav_data['favtime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(favtime))
        created_at = time2timestamp(fav['status']['created_at'])
        fav_data['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_at))
        fav_data['post_text'] = fav['status']['text']
        fav_data['pic_urls'] = json.dumps(fav['status']['pic_urls']) if fav['status'].has_key('pic_urls') else json.dumps([])
        try:
            fav_data['user_id'] = fav['status']['user']['id']
        except Exception, e:
            deleted += 1
            continue
        # 个人微博主页
        fav_data['profile_url'] = "http://weibo.com/%s" % fav['status']['user']['profile_url']
        fav_data['profile_image_url'] = fav['status']['user']['profile_image_url']
        fav_data['screen_name'] = fav['status']['user']['screen_name']
        # 个人主页，即使没有也会返回 ""
        fav_data['url'] = fav['status']['user']['url'] if fav['status']['user']['url'] else fav_data['profile_url']

        if fav['status'].has_key('retweeted_status'):
            # 处理微博被删的情况
            if fav['status']['retweeted_status'].has_key('deleted') and fav['status']['retweeted_status']['deleted'] == "1":
                deleted += 1
                continue

            re_created_at = time2timestamp(fav['status']['retweeted_status']['created_at'])
            fav_data['re_created_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(re_created_at))
            fav_data['re_post_text'] = fav['status']['retweeted_status']['text']
            fav_data['re_id'] = fav['status']['retweeted_status']['id']
            fav_data['re_pic_urls'] = json.dumps(fav['status']['retweeted_status']['pic_urls']) if fav['status']['retweeted_status'].has_key('pic_urls') else json.dumps([])
            fav_data['re_user_id'] = fav['status']['retweeted_status']['user']['id']
            fav_data['re_profile_url'] = "http://weibo.com/%s" % fav['status']['retweeted_status']['user']['profile_url']
            fav_data['re_profile_image_url'] = fav['status']['retweeted_status']['user']['profile_image_url']
            fav_data['re_screen_name'] = fav['status']['retweeted_status']['user']['screen_name']
            fav_data['re_url'] = fav['status']['retweeted_status']['user']['url'] if fav['status']['retweeted_status']['user']['url'] else fav_data['re_profile_image_url']

        favorites.append(fav_data)

        # like "tags": [ {'id': 23, 'tag': "good"}, ... ]
        if len(fav['tags']) > 0:
            for tag in fav['tags']:
                tags[tag['id']] = tag['tag']

                if not posts_tags.has_key(fav_data['id']):
                    posts_tags[fav_data['id']] = []
                posts_tags[fav_data['id']].append(tag['id'])

    content = json.dumps(tags)
    content += '</br></br>' + json.dumps(posts_tags)
    # 入库, posts & tags & posts_tags
    dbutils.insertPosts(favorites)
    dbutils.insertTags(tags)
    dbutils.insertPostsTags(posts_tags)


# intime like 'Tue Jan 06 03:16:04 +0800 2015'
def time2timestamp(intime):
    # like 'Tue Jan 06 03:16:04 2015'
    intime = intime[0:-10] + intime[-4:]
    return time.mktime(time.strptime(intime, "%a %b %d %H:%M:%S %Y"))


if __name__ == '__main__':
    import sys
    token = sys.argv[1]
    expire = sys.argv[2]

    client = _create_client()
    client.set_access_token(token, expire)
    load_raw_posts(client)
