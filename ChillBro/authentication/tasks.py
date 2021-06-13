from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from celery.decorators import task
from ChillBro.celery import debug_task, app
from celery.utils.log import get_task_logger
from django.conf import settings
from datetime import datetime, timedelta
import pytz
logger = get_task_logger(__name__)


@task(name="send_email")
def send_multi_format_email(template_prefix, template_ctxt, target_email):
    current_time = datetime.utcnow()
    current_time.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
    debug_task.apply_async((), eta=current_time + timedelta(seconds=50))
    logger.info("Sent feedback email" + str(current_time))

    subject_file = 'authentication/%s_subject.txt' % template_prefix
    txt_file = 'authentication/%s.txt' % template_prefix
    html_file = 'authentication/%s.html' % template_prefix

    subject = render_to_string(subject_file).strip()
    from_email = settings.EMAIL_FROM
    to = target_email
    bcc_email = settings.EMAIL_BCC
    text_content = render_to_string(txt_file, template_ctxt)
    html_content = render_to_string(html_file, template_ctxt)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to],
                                 bcc=[bcc_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
