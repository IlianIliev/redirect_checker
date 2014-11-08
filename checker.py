#!/usr/bin/env python
import datetime
import logging
import requests
import smtplib



logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


URLS_TO_TEST = [
    # tuple with the following format (url, status_code, redirect_url)
    ('http://httpstatuscodes.appspot.com/200/', 200),
    ('http://httpstatuscodes.appspot.com/404/', 404),
    ('http://httpstatuscodes.appspot.com/500/', 500),
    ('http://httpstatuscodes.appspot.com/301/', 301, 'httpstatuscodes.appspot.com/200/'),
    ('http://httpstatuscodes.appspot.com/302/', 302, 'httpstatuscodes.appspot.com/200/')

]


errors = []

logger.debug('Started: {}'.format(datetime.datetime.utcnow()))

for item in URLS_TO_TEST:
    logger.debug('-' * 80)

    url = item[0]
    expected_status = item[1]

    logger.debug('Checking {}'.format(url))

    try:
        response = requests.get(url)
        if response.status_code != expected_status:
            errors.append('URL {} returns {} instead of {}'.format(url, response.status_code, expected_status))
        elif expected_status in [301, 302]:
            try:
                expected_redirect = item[2]
            except IndexError:
                errors.append('URL {} return redirect({}) but no redirect URL has been specified.'.format(
                    url, response.status_code))
            else:
                if response.url != expected_redirect:
                    errors.append('URL {} redirects to {} instead of {}.'.format(url, response.url, expected_redirect))
    except Exception, e:
        logger.info(e)

logger.debug('-' * 80)
logger.debug('Completed: {}'.format(datetime.datetime.utcnow()))

if errors:
    logger.error('Errors found')
    for record in errors:
        logger.error(record)

    # sending emails
    sender = 'test@localhost'
    receiver = ['ilian@i-n-i.org']

    subject = 'Blacklisted !!!'
    message = """
        Blacklisted:\n
        {}\n\n
    """.format('\n'.join(errors))

    try:
       smtp_obj = smtplib.SMTP('localhost')
       smtp_obj.sendmail(sender, receiver, message)
       logger.debug('Successfully sent email')
    except smtplib.SMTPException:
       logger.error('Error: unable to send email')
