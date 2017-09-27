'''
依赖库：
    python-wordpress-xmlrpc (2.3)

说明：
    IceWarp　本身支持rpc接口,该接口是用php写的，用python调用比较困难，所有写下
此此接口．　IceWarpAPI　是简单的封装了下api, IceWarpProxy 是连接rpc的封装．
Icewarp　则是对目前的需求进行的封装（账号添加）

要修改里面的类请到官网阅读api里的php章节

'''

import xmlrpc.client


class NullPointerException(Exception):
    pass


class NoSuchDomainException(Exception):
    pass

AccountType = {
    '0':'POP3',
    '1':'IMAP & POP3',
    '2':'IMAP'
}

class IceWarpProxy(object):
    _types_ = {
        "None->Create": "APIObject",
        "APIObject->NewDomain": "DomainObject",
        "APIObject->OpenDomain": "DomainObject",
        "DomainObject->NewAccount": "AccountObject",
        "DomainObject->OpenAccount": "AccountObject",
        "APIObject->GetDomainList": "DomainObject",
    }

    def __init__(self, api, ptr, type):
        self.api = api
        self.ptr = ptr
        self.type = type or "None"

    @classmethod
    def new(self, api, ptr, type):
        if ptr and ptr != "0":
            return self(api, ptr, type)
        else:
            return None

    def __getattr__(self, name):
        func = getattr(self.api.xmlrpc_proxy, "%s->%s" % (self.ptr, name))
        if self.type is None and name == "Create":
            def wrap(*args):
                if len(args):
                    type = args[0].split(".")[-1]
                else:
                    type = None
                ptr = func(*args)
                return IceWarpProxy.new(self.api, ptr, type)

            return wrap
        else:
            type = self._types_.get("%s->%s" % (self.type, name))
            if type:
                def wrap(*args):
                    getattr(self.api.xmlrpc_proxy, "%s->%s" % (self.ptr, name))
                    ptr = func(*args)

                    return IceWarpProxy.new(self.api, ptr, type)

                return wrap
            else:
                return func

    def __repr__(self):
        return "<IceWarpProxy [%s %r]>" % (self.type, self.ptr)



class IceWarpAPI(object):
    def __init__(self, api_url):
        self.xmlrpc_proxy = xmlrpc.client.ServerProxy(api_url)
        self.null_object = IceWarpProxy(self, "0", None)
        self.api_object = self.null_object.Create("IceWarpServer.APIObject")

        self._domains = {}
        self._accounts = {}

    def __getattr__(self, name):
        return getattr(self.api_object, name)

    def OpenDomain(self, domain):
        if domain not in self._domains:
            self._domains[domain] = self.api_object.OpenDomain(domain)
        return self._domains[domain]

    def OpenAccount(self, domain, alias):
        acct = "%s@%s" % (domain, alias)
        if acct not in self._accounts:
            domain_object = self.OpenDomain(domain)
            if not domain_object:
                raise NoSuchDomainException(domain)
            self._accounts[acct] = domain_object.OpenAccount(alias)
        return self._accounts[acct]



class Icewarp(object):
    def __init__(self, server=None, login=None, password=None):
        api_creds = {"login": login, "password": password, "machine": server}
        try:
            api_base = "https://%(login)s:%(password)s@%(machine)s/rpc/" % api_creds
            self.api = IceWarpAPI(api_base)
        except:
            api_base = "http://%(login)s:%(password)s@%(machine)s/rpc/" % api_creds
            self.api = IceWarpAPI(api_base)

    def get_account_list(self, domain):
        '''
        获取账号列表
        :param domain:
        :return:
        '''
        domain_list = self.api.OpenDomain(domain).GetAccountList()
        return domain_list.split(';')

    def get_account_info(self,domain, account):
        '''
        获取账号信息
        :param domain:
        :param account:
        :return:
        '''
        account_obj = self.api.OpenAccount(domain,account)
        info = dict()
        if account_obj:
            info['passwd'] = account_obj.GetProperty("U_Password")
            info['alias'] = account_obj.GetProperty("U_Alias")
            info['mailbox'] = account_obj.GetProperty("U_Mailbox")
            info['comment'] = account_obj.GetProperty("U_Comment")
            # info['LoginWithFullAddress'] = account_obj.GetProperty("LoginWithFullAddress")
        return info

    def create_account(self,domain,alias,name,password,Comment):
        '''
        创建账号
        :param domain:
        :param alias:
        :param name:
        :param password:
        :param Comment:
        :return:
        '''
        DomainObj = self.api.OpenDomain(domain)
        if not DomainObj:
            raise NoSuchDomainException(domain)
        NewAccount = DomainObj.NewAccount(alias)
        NewAccount.SetProperty('u_name', name)
        NewAccount.SetProperty('u_password', password)
        NewAccount.SetProperty('U_Comment', Comment)
        print(NewAccount.Save())

        if eval(NewAccount.Save()):
            return {'statu':True,'code':'账号创建成功'}
        else:
            if self.alias_exist(domain, alias):
                return {'statu': False, 'info': '有相同账号存在，创建失败'}
            else:
                return {'statu': False, 'info': '账号创建失败'}

    def updateMailAccountPwd(self, domain, alias, password):
        '''
        更新密码
        :param domain:
        :param alias:
        :param password:
        :return:
        '''
        AccountObj = self.api.OpenAccount(domain, alias)
        if not AccountObj:
            return {'statu':False,'info':'账号不存在'}
        AccountObj.SetProperty('u_password', password)
        if eval(AccountObj.Save()):
            return {'statu':True,'info':'账号密码已经更新'}
        else:
            return {'statu': False, 'info': '账号存在异常'}


    def alias_exist(self, domain,alias):
        '''
        判断账号是否存在
        :param domain: 账号
        :param alias:
        :return:
        '''
        DomainObj = self.api.OpenDomain(domain)
        # 试图找到域中的别名，如果找到索引将返回，如果不是负数将返回。
        # 参数可以只包含别名，在这种情况下对象的域名将被使用，也可以包含完整的电子邮件地址。
        index = DomainObj.GetAccountIndexByAlias(alias)
        return int(index)>-1

    def delete_account(self,domain,alias):
        '''
        删除账号
        :param domain:
        :param alias:
        :return:
        '''
        DomainObj = self.api.OpenDomain(domain)
        if not DomainObj:
            raise NoSuchDomainException(domain)
        status = DomainObj.DeleteAccount(alias)
        return eval(status)


    def GetAccountIndexByComment(self,domain,comment):
        '''
        根据说明（描述／工号）获取账号详情　　模糊查询
        :param domain:
        :param comment:
        :return:
        '''
        account = ice.api.OpenDomain(domain).NewAccount()
        # FindInitQuery 功能做了与 FindInit 功能相同的工作，除非它接受一个查询参数，通过 Meeting 让您的标准帐户进行循
        # 环。该查询使用 SQL 语法，并支持文件系统帐户，数字参数应该像对待字符串，始终使用分组括号，LIKE 运算符也支
        # 持在文件系统帐户模式。
        # $account->FindInitQuery("test.com", "(u_alias like '%john%') or (u_admin = '1')");
        Query_statu = account.FindInitQuery(domain, "U_Comment like '%"+comment+"%'")
        ret = []
        while eval(account.FindNext()):
            row = dict()
            row['u_alias']=account.GetProperty("u_alias")
            row['u_name']=account.GetProperty("u_name")
            row['U_Comment'] = account.GetProperty("U_Comment")
            # row['u_password'] = account.GetProperty("u_password")
            # row['u_admin'] = account.GetProperty("u_admin")!='0'
            # row['u_account'] = AccountType[account.GetProperty("u_account")]
            # row['U_PhoneAlias'] = account.GetProperty("U_PhoneAlias")
            # row['U_Mailbox'] = account.GetProperty("U_Mailbox")
            ret.append(row)
        #　关闭查询
        account.FindDone()
        return ret

    def GetAccountIndexByAlias(self,domain,alias):
        '''
        根据账号获取账号详情　　模糊查询
        :param domain:
        :param alias:
        :return:
        '''
        account = ice.api.OpenDomain(domain).NewAccount()
        # FindInitQuery 功能做了与 FindInit 功能相同的工作，除非它接受一个查询参数，通过 Meeting 让您的标准帐户进行循
        # 环。该查询使用 SQL 语法，并支持文件系统帐户，数字参数应该像对待字符串，始终使用分组括号，LIKE 运算符也支
        # 持在文件系统帐户模式。
        # $account->FindInitQuery("test.com", "(u_alias like '%john%') or (u_admin = '1')");
        Query_statu = account.FindInitQuery(domain, "u_alias = '" + alias + "'")
        ret = []
        while eval(account.FindNext()):
            row = dict()
            row['u_alias'] = account.GetProperty("u_alias")
            row['u_name'] = account.GetProperty("u_name")
            row['U_Comment'] = account.GetProperty("U_Comment")
            # row['u_password'] = account.GetProperty("u_password")
            # row['u_admin'] = account.GetProperty("u_admin")!='0'
            # row['u_account'] = AccountType[account.GetProperty("u_account")]
            # row['U_PhoneAlias'] = account.GetProperty("U_PhoneAlias")
            row['U_Mailbox'] = account.GetProperty("U_Mailbox")
            ret.append(row)
        # 关闭查询
        account.FindDone()
        return ret

if __name__ == '__main__':
    ice = Icewarp(server='172.16.74.192', login='admin', password='Vasd.asd.')
    data = ice.alias_exist('test.com','yuyuan')
    print(data)


