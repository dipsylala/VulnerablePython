import sqlite3
import subprocess
import os
import yaml
import requests

# CWE-798: Hardcoded credentials
DB_PASSWORD = "supersecret123"
SECRET_KEY = "hardcoded-secret-key-do-not-use"

def get_db():
    conn = sqlite3.connect("users.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
    )
    return conn


def get_user(username):
    conn = get_db()
    cursor = conn.cursor()
    # CWE-89: SQL Injection — user input concatenated directly into query
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()


def ping_host(host):
    # CWE-78: OS Command Injection — unsanitized input passed to shell
    result = subprocess.run("ping -c 1 " + host, shell=True, capture_output=True, text=True)
    return result.stdout


def run_script(user_input):
    # CWE-95: Code Injection — eval on untrusted input
    return eval(user_input)


def load_config(config_str):
    # CWE-502: Deserialization of untrusted data — yaml.load() without Loader
    # Exploitable in PyYAML < 6.0 (CVE-2020-14343)
    return yaml.load(config_str)


def fetch_url(url):
    # Uses requests 2.6.0, vulnerable to session fixation (CVE-2015-2296)
    return requests.get(url)


if __name__ == "__main__":
    print("Looking up user:", get_user("admin"))
    print("Pinging host:", ping_host("localhost"))
