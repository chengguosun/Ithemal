#!/usr/bin/python

import argparse
import json
import subprocess
import urllib2
import os
from typing import Optional

WEBHOOK_URL = 'https://hooks.slack.com/services/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'
SLACK_USERNAME = 'AWS'
SLACK_CHANNEL = 'aws-notifications'
SLACK_ICON = 'https://raw.githubusercontent.com/quintessence/slack-icons/e9e141f0a119759ca4d59e0b788fc9375c9b2678/images/amazon-web-services-slack-icon.png'

# map from IAM key to Slack user ID
USER_MAP = {
    'renda': 'UCJ98TMB8',
    'charithm': 'UB59J5BHR',
    'mcarbin': 'U7QK3FX88',
}

def get_starting_user():
    # type: () -> Optional[str]
    '''Get the IAM key (user) that started this AWS instance, or None if this is not an AWS instance
    '''
    proc = subprocess.Popen(
        ['/usr/bin/curl', '--silent', '--connect-timeout', '1', 'http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key'],
        stdout=subprocess.PIPE,
        stderr=open(os.devnull, 'w'),
    )
    proc.wait()
    if proc.returncode:
        return None

    stdout, _ = proc.communicate()
    stdout = stdout.strip()
    return stdout.split()[2]

def send_message(message):
    # type: (str) -> None
    ''' Send the given message to slack
    '''
    payload = {
        'text': message,
        'username': SLACK_USERNAME,
        'icon_url': SLACK_ICON,
        'channel': SLACK_CHANNEL,
    }

    request = urllib2.Request(WEBHOOK_URL, json.dumps(payload))
    urllib2.urlopen(request)

def main():
    # type: () -> None
    parser = argparse.ArgumentParser(description='Ping a user in the #aws-notifications channel on Slack')
    parser.add_argument('--user', default=None, help='User to ping (default: user that started instance on AWS)')
    parser.add_argument('message', help='Message to send')

    # behave like 'echo', and just concatenate all args (undocumented)
    args, unknown_args = parser.parse_known_args()

    message = args.message
    for unknown_arg in unknown_args:
        message += ' ' + unknown_arg

    user = args.user or get_starting_user()

    # if there is a user, taf them
    if user:
        message = '<@{}>: {}'.format(
            USER_MAP[user],
            message,
        )

    send_message(message)

if __name__ == '__main__':
    main()
