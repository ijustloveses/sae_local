1. 使用 textpad 修改 hosts ，加入 $localip marked.sinaapp.com
2. sudo killall -9 nginx && sudo python2.7 server.py
3. 浏览器中访问 $localip/signin，等待转向到 getauthinfo 页面，会展示 auth_token 和 expired_time
4. 在数据库 sae_marked 中可以看到 users 表中的 expired_time 会被调整为新的过期时间
```
+------------+--------+----------------------------------+--------------+
| id         | name   | auth_token                       | expired_time |
+------------+--------+----------------------------------+--------------+
| xxx        | xxx    | xxxxxxxxxxxxxxxxxxxxxx           |   1626838595 |
+------------+--------+----------------------------------+--------------+
```
5. 打开 postloader.py 修改几个参数
  - _MIN_POST_ID：上次更新后的最大的 post id，也就是本次更新的 post id 都要比这个值大才合理
  - _START 、 _END：本次更新的分页范围，前闭后开；代码中默认每页 50 个 posts，需要计算一下来设置
6. 运行 python2.7 postloader.py ${auth_token} ${expired_time}
