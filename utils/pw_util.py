import os

LOCAL_ASSETS = "local_assets"
PW_FILE_NAME = "pw.txt"
CONFIG_FILE_NAME = 'config.cfg'


def get_user_password():
    if not os.path.exists(LOCAL_ASSETS):
        os.makedirs(LOCAL_ASSETS)
    pw_file_path = os.path.join(LOCAL_ASSETS, PW_FILE_NAME)
    if not os.path.exists(pw_file_path):
        user = input("Please input login name:")
        password = input("Please input login password:")
        with open(pw_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{user}\n{password}")
    else:
        with open(pw_file_path, 'r', encoding='utf-8') as f:
            (user, password) = f.read().strip().split('\n')
    return (user, password)


def load_config():
    if not os.path.exists(LOCAL_ASSETS):
        os.makedirs(LOCAL_ASSETS)
    config_file_path = os.path.join(LOCAL_ASSETS, CONFIG_FILE_NAME)
    if not os.path.exists(config_file_path):
        # user = input("Please input login name:")
        # password = input("Please input login password:")
        # with open(config_file_path, 'w', encoding='utf-8') as f:
        #     f.write(f"{user}\n{password}")
        pass
    else:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            (user, password) = f.read().strip().split('\n')
    # return (user, password)
