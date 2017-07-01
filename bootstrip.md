vultr + shadowsocks
======================
http://www.jianshu.com/p/4bf38b9d5d78

然后关掉 firewalld
systemctl stop firewalld.service
systemctl disable firewalld.service

改用 iptables
yum install iptables-services
编辑配置文件
vim /etc/sysconfig/iptables
```
-A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
-A INPUT -p udp -m state --state NEW -m udp --dport 6000 -j ACCEPT
-A INPUT -p udp -m state --state NEW -m udp --dport 1081 -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 6000 -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 1081 -j ACCEPT
```
启动
systemctl restart iptables.service
systemctl enable iptables.service


启动 python web server
=======================

yum install git

yum install mariadb mariadb-server mysql-devel gcc python-devel
systemctl start mariadb
systemctl enable mariadb
mysql_secure_installation
mysql -uroot -p${pass}

pip install gunicorn
pip install mysqlclient

修改 iptables 配置
```
-A INPUT -p tcp -m state --state NEW -m tcp --dport 8000 -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 8080 -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 8008 -j ACCEPT
```

gunicorn server:app -w 2 -b 0.0.0.0:8000 -D
