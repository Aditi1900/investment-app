import bcrypt

# INPUT: 
#   -credentials(tuple[str,str]); user login and password
# OUTPUT: None
# PRECONDITION:
#   -credentials; login and password are non-empty strings, see Validator.account_validator() POSTCONDITION
# POSTCONDITION: 
#   -credentials; password is properly hashed and repacked into credentials with the hashed string replacement
# RAISES: None
def secure_creds(credentials : tuple[str, str]) -> tuple[str, str]:
    password = credentials[1]
    salt = bcrypt.gensalt()

    password = bcrypt.hashpw(password.encode('utf-8'), salt)

    credentials = credentials[0], password.decode('utf-8')

    return credentials


# INPUT: 
#   -plain(str); a plaintext password
#   -hashed(str); a previously hashed password
# OUTPUT:
#   -match(bool); True or False, password match
# PRECONDITION:
#   -hashed; contains unique salt
# POSTCONDITION: 
#   -match; passwords are properly identified as matching or not
# RAISES: None
def password_match(plain : str, hashed : str) -> bool:
    match = bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    return match