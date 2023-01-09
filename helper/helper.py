"""
Helper script for some utilities
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from pydantic import EmailStr
from fastapi import Depends
from jose import jwt
import emails
from emails.template import JinjaTemplate
from core import config

file_path: Path = Path("./openapi.json")
TELEPHONE_REGEX: str = r"\(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5}?-?" \
                       r"[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?"
password_regex: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?" \
                      r"[#?!@$%^&*-]).{8,14}$"


# TODO: Update emails methods (third-party library) to email (built-in)
#  and add docstrings.

# https://docs.python.org/3/library/email.examples.html
# https://gist.github.com/perfecto25/4b79b960eb58dc1f6025b56394b51cc1
# Email Exceptions:
# - email.errors.HeaderParseError
# - email.errors.MultipartConversionError
# - MalformedHeaderDefect
# JinjaTemplate Exceptions:
# - jinja2.UndefinedError
# - jinja2.TemplateNotFound
# - jinja2.TemplateSyntaxError
# - jinja2.TemplateRuntimeError
# - jinja2.TemplateAssertionError
# JWT Exceptions
# - jwt.exceptions.InvalidTokenError
# - jwt.exceptions.DecodeError
# - jwt.exceptions.InvalidSignatureError
# - jwt.exceptions.ExpiredSignatureError
# - jwt.exceptions.InvalidIssuerError
# - jwt.exceptions.InvalidIssuedAtError
# - jwt.exceptions.InvalidKeyError
# - jwt.exceptions.InvalidAlgorithmError
# - jwt.exceptions.MissingRequiredClaimError

async def update_json() -> None:
    """
    Generate JSON file
    :return: None
    :rtype: NoneType
    """
    openapi_content: dict = json.loads(file_path.read_text(encoding='UTF-8'))
    for key, path_data in openapi_content["paths"].items():
        if key == '/':
            continue
        for operation in path_data.values():
            tag: str = operation["tags"][0]
            operation_id: str = operation["operationId"]
            to_remove: str = f"{tag}-"
            # new_operation_id = operation_id[len(to_remove):]
            new_operation_id = operation_id.removeprefix(to_remove)
            operation["operationId"] = new_operation_id
    # print(json.dumps(openapi_content, indent=4))
    file_path.write_text(json.dumps(openapi_content), encoding='UTF-8')


async def send_email(
        email_to: EmailStr, subject_template: str = "",
        html_template: str = "", environment: dict[str, Any] = None,
        setting: config.Settings = Depends(config.get_setting)) -> None:
    """
    Send email method to recipient with specific data from HTML template
    :param email_to: recipient email
    :type email_to: EmailStr
    :param subject_template: Template for email subject
    :type subject_template: str
    :param html_template: Template for HTML
    :type html_template: str
    :param environment: Environment data to add to email
    :type environment: dict
    :param setting: Settings to configure email process
    :type setting: Settings
    :return: None
    :rtype: NoneType
    """
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(setting.EMAILS_FROM_NAME, setting.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": setting.SMTP_HOST, "port": setting.SMTP_PORT}
    if setting.SMTP_TLS:
        smtp_options["tls"] = True
    if setting.SMTP_USER:
        smtp_options["user"] = setting.SMTP_USER
    if setting.SMTP_PASSWORD:
        smtp_options["password"] = setting.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info("send email result: %s", response)


async def send_test_email(
        email_to: EmailStr, setting: config.Settings = Depends(config.get_setting)
) -> None:
    """
    Sent test email using environment vars
    :param email_to: recipient email
    :type email_to: EmailStr
    :param setting: Settings to configure email process
    :type setting: Settings
    :return: None
    :rtype: NoneType
    """
    project_name = setting.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(setting.EMAIL_TEMPLATES_DIR) / "test_email.html",
              encoding='UTF-8') as file:
        template_str = file.read()
    await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"PROJECT_NAME": setting.PROJECT_NAME, "email": email_to},
        setting=setting
    )


async def send_reset_password_email(
        email_to: EmailStr, email: str, token: str,
        setting: config.Settings = Depends(config.get_setting)) -> None:
    """
    Send reset password email to user given its info and token
    :param email_to: recipient email
    :type email_to: EmailStr
    :param email: Owner of e-mail
    :type email: str
    :param token: access token
    :type token: str
    :param setting: Settings to configure email process
    :type setting: Settings
    :return: None
    :rtype: NoneType
    """
    project_name = setting.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(setting.EMAIL_TEMPLATES_DIR) / "reset_password.html",
              encoding='UTF-8') as file:
        template_str = file.read()
    base_url = setting.SERVER_HOST
    link = f"{base_url}/reset-password?token={token}"
    await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "PROJECT_NAME": setting.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": setting.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        }, setting=setting
    )


async def send_new_account_email(
        email_to: EmailStr, username: str,
        setting: config.Settings = Depends(config.get_setting)) -> None:
    """
    Send e-mail confirmation about new account created to user
    :param email_to: recipient email
    :type email_to: EmailStr
    :param username: Username
    :type username: str
    :param setting: Settings to configure email process
    :type setting: Settings
    :return: None
    :rtype: NoneType
    """
    project_name = setting.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(setting.EMAIL_TEMPLATES_DIR) / "new_account.html",
              encoding='UTF-8') as file:
        template_str = file.read()
    link = setting.SERVER_HOST
    await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "PROJECT_NAME": setting.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "link": link,
        }, setting=setting
    )


async def generate_password_reset_token(
        email: str, setting: config.Settings = Depends(config.get_setting)
) -> str:
    """
    Generate password to reset token
    :param email:
    :type email:
    :param setting: Settings to configure email process
    :type setting: Settings
    :return: None
    :rtype: NoneType
    """
    delta = timedelta(hours=setting.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    # Fixme: Update encoding
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, setting.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


async def verify_password_reset_token(
        token: str, setting: config.Settings = Depends(config.get_setting)
) -> Optional[str]:
    """
    Decoding JWT to verify password and reset it.
    :param token: JWT generated at login
    :type token: str
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :return: email retrieved from JWT
    :rtype: str
    """
    try:
        decoded_token = jwt.decode(
            token=token, key=setting.SECRET_KEY,
            algorithms=[setting.ALGORITHM], options={"verify_subject": False},
            audience=setting.SERVER_HOST + '/authentication/login',
            issuer=setting.SERVER_HOST)
        return decoded_token["email"]
    except jwt.JWTError:
        return None
