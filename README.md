# icewarp
IceWarp sdk

本项目是基于爱思华宝提供的rpc api来实现的，主要作用则是账号创建，当然也有很多其他接口，
理论上官方提供的接口都能实现的，因为官方的rpc服务是php写的，所以要扩展请查看官网的php
相关的api，由于是直接调用的rpc接口，本库只是做了调用和数据格式的转换，将不负责调用产生
的安全问题．

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