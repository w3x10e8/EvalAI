import json
import logging
import requests
import traceback

from django.conf import settings
from django.core.mail import send_mail

from evalai.celery import app

from smtplib import SMTPException

logger = logging.getLogger(__name__)


@app.task
def notify_admin_on_receiving_contact_message(webhook_url, name, email, message):
    '''
    Send email and slack notification to EvalAI Admin
    whenever someone submits a contact message
    '''
    # Send slack notification
    data = {
        'text': '*{} ({})* has sent a message \n *{}*'.format(name, email, message)}
    header = {'Content-type': 'application/json'}
    try:
        response = requests.post(
            webhook_url, headers=header, data=json.dumps(data))
        logger.info("Notification successfully sent to slack with status code {}!".format(
            response.status_code))
    except requests.exceptions.HTTPError:
        logger.exception(traceback.format_exc())

    # Send email to EvalAI Admin
    from_email = settings.EMAIL_HOST_USER
    subject = "EvalAI contact message received from {}".format(name)
    to_email = [settings.ADMIN_EMAIL]
    try:
        send_mail(subject, message, from_email, to_email)
        logger.info("Email successfully sent to EvalAI Admin!")
    except SMTPException:
        logger.exception(traceback.format_exc())