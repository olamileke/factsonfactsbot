from dotenv import load_dotenv
import os.path as path

base_dir = path.abspath(path.dirname(__file__))

def set():
    env_path = path.join(base_dir, '.env')
    load_dotenv(env_path)