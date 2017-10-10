# icewarp
IceWarp sdk

本项目是基于爱思华宝提供的rpc api来实现的，主要作用则是账号创建，域名创建等。
查询的邮箱信息等则不再提供。觉得直接连接数据库会查询得更快。

使用环境
----
+ `python3.5`测试通过

安装
----
`pip install git+https://github.com/Apuyuseng/icewarp.git`

使用
----


```python
>>>import icewarp
>>>c = icewarp.connect('https://user:account@host/rpc/')
>>>c.get_account_info('test.com','yuyuan') #　获取帐号信息
{'alias': 'yuyuan',
 'comment': 'this is test',
 'mailbox': 'yuyuan',
 'passwd': 'Csadzx214'}

>>>c.GetDomainList() # 获取域列表
['test.com','qq.com']
```