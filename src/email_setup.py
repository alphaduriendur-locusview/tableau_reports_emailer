import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import json
import base64


class NoticeEmail:
    '''Class representing a Sendgrid email'''

    def __init__(self, msg_subject, msg_content, msg_attachment, msg_filename, msg_to=['kyle.surowiec@locusview.com', 'casey.mullan@locusview.com', 'fred.scholcoff@locusview.com'], msg_from='notifications@locusview.com'):
        with open('email_config.json', 'r') as config:
            data = json.load(config)
        key = data['sendgrid']

        self.test_list = data['testEmails']
        self.is_test = data['test']
        self.sg = sendgrid.SendGridAPIClient(os.environ.get('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'))
        self.to_email = msg_to
        self.from_email = msg_from
        self.subject = msg_subject
        self.content = msg_content
        self.attachment = msg_attachment
        self.filename = msg_filename

        print("Inside constructor")

        self.data = {
            "personalizations": [
                {
                    "to": self._create_email_list(),
                    "subject": self.subject
                }
            ],
            "from": {
                "email": self.from_email,
                "name": "LocusView Notifications"
            },
            "content": [
                {
                    "type": "text/html",
                    "value": self.content
                }
            ],
            "attachments": [
                {
                    "content": self._create_attachment(self.attachment),
                    "filename": self.filename,
                    "disposition": "attachment"
                }
            ]
        }
        print("Creating Sendgrid Mail Object")
        try:
            self.attachedFile = Attachment(
                FileContent(self._create_attachment(self.attachment)),
                FileName(self.filename),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            self.message = Mail(
                from_email=Email(email=self.from_email,name="LocusView Notifications"),
                to_emails=self._create_email_list(),
                subject=self.subject,
                plain_text_content=Content("text/html", self.content)
            )
            self.message.attachment = self.attachedFile
            print("Mail Object created successfully!")
        except Exception as e:
            print("Error: \n{}".format(e))

    def _create_attachment(self, file_path):
        try:
            with open(self.attachment, 'rb') as f:
                data = f.read()
                f.close()
            data = base64.b64encode(data).decode()
            print("Decode success!")
            return data
        except Exception as e:
            print("Failure in creating attachment!")
            print(e)

    def _create_email_list(self):
        emails = []
        emails2 = []

        if self.is_test == 'true':
            email_list = self.test_list
        else:
            email_list = self.to_email

        for email in email_list:
            temp = {
                "email": email
            }
            temp_to_email = To(email)
            emails.append(temp)
            emails2.append(temp_to_email)
        print("Email List: {}".format(emails2))
        return emails2

    def send_mail(self):
        try:
            res = self.sg.send(self.message)
            print(res.status_code, res.body, res.headers)
        except Exception as e:
            print("Send Email FAILURE: \n{}".format(e))
