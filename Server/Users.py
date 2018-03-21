from collections import namedtuple

defaultPassword = 'Default'
defaultAccount = 'None'

UserInfo = namedtuple("UserInfo", "password account")
UserInfo.__new__.__defaults__ = (defaultPassword, defaultAccount)

users = {
    'Benjy': UserInfo(password = 'Hello'),
    'Shane': UserInfo(account = 'Wits'),
    'Test': UserInfo(password = 'Whaddup', account = 'Wits'),
    'anonymous': UserInfo(),
}
print users['Shane'].password
