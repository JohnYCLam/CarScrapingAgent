from __future__ import annotations

from botocore.exceptions import ClientError

from car_agent.config import Settings


class Emailer:
    def __init__(self, ses_client, settings: Settings):
        self._ses = ses_client
        self._settings = settings

    def send_email(self, to_email: str, subject: str, body: str) -> None:
        try:
            self._ses.send_email(
                Source=self._settings.from_email,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
        except ClientError as e:
            print(f"Error sending email: {e}")
