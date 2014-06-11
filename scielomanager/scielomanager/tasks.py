from __future__ import absolute_import
import logging

from django.conf import settings
from django.core.mail import EmailMessage

from scielomanager.celery import app

logger = logging.getLogger(__name__)

@app.task(bind=True)
def send_mail(self, subject, content, to_list, html=True):
    """
    Send email to list set on ``to_list`` param.
    This tasks consider the settings.DEFAUL_FROM_EMAIL as from_mail param

    :param subject: A string as subject
    :param content: A HTML or a plain text content
    :param to_list: A list or tuple with the e-mails to send message
    :param html: Boolean to send as HTML or plain text, default is HTML

    Return the result of django.core.mail.message.EmailMessage.send

    If any exception occurred the task will be re-executed in 3 minutes until
    default max_retries 3 times, all are celery default params
    """

    msg = EmailMessage(subject, content, settings.DEFAULT_FROM_EMAIL, to_list)

    if html:
        msg.content_subtype = 'html'

    try:
        ret = msg.send()
        logger.info("Successfully sent email message to {0!r}.".format(to_list))
        return ret
    except Exception as e:
        logger.error("Failed to send email message to {0!r}, traceback: {1!s}".format(to_list, e))
        raise self.retry(exc=e)
