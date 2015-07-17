class UserCreate_SHORT(Exception):
  def __init__(self):
    self.msg = 'The length of password should contain at least 6 characters.'

class UserCreate_LONG(Exception):
  def __init__(self):
    self.msg = 'The length of password should contain at most 15 characters.'

class UserCreate_NOINST(Exception):
  def __init__(self):
    self.msg = 'Institution is required.'

class UserCreate_NONAME(Exception):
  def __init__(self):
    self.msg = 'Name is required.'

class UserCreate_REPEMAIL(Exception):
  def __init__(self):
    self.msg = 'E-mail address has been used. Please use another one'

class Login_NOUSER(Exception):
  def __init__(self):
    self.msg = 'E-mail or password is wrong. Please try again.'

class Login_WRONGPW(Exception):
  def __init__(self):
    self.msg = 'E-mail or password is wrong. Please try again.'

class Login_NOTVERIFIED(Exception):
  def __init__(self):
    self.msg = 'Account has not been verified. Another verification email has been sent to your.'

class VerifyEmail_NOUSER(Exception):
  pass

class VerifyEmail_EXPIRED(Exception):
  pass

class VerifyEmail_FAILDED(Exception):
  pass

