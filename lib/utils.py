import sys
import getpass

def get_password_and_username():
    """Gets the user's ESO-user password to access the p2ui"""
    username = input("Input your ESO-username")
    password_prompt = f'Input your ESO-password: '
    if sys.platform == 'ios':
        import console
        password = console.password_alert(password_prompt)
    elif sys.stdin.isatty():
        password = getpass.getpass(password_prompt)
    else:
        password = input()
    return username, password


if __name__ == "__main__":
    ...

