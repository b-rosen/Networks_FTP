from collections import namedtuple

''' All Code in this file is Written by Benjamin Rosen (858324) '''

defaultPassword = 'Default'
defaultAccount = 'None'

UserInfo = namedtuple("UserInfo", "password account")
UserInfo.__new__.__defaults__ = (defaultPassword, defaultAccount)

# A dictionary containing the relevant information for each user. Different levels of access can be assigned to each user (password, account or both).
users = {
    'Benjy': UserInfo(password = 'Hello'),
    'Shane': UserInfo(account = 'Wits'),
    'Test': UserInfo(password = 'Whaddup', account = 'Wits'),
    'anonymous': UserInfo(),
}
