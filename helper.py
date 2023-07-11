import json
import logging
import os.path
from json import JSONDecodeError

import allure
import requests.exceptions
from allure_commons._allure import step
from allure_commons.types import AttachmentType
from requests import Session, Response
import curlify


def load_json_schema(name: str):
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schemas', name)
    with open(schema_path) as schema:
        return json.loads(schema.read())


class CustomSession(Session):
    def __init__(self, base_url):
        self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs) -> Response:
        response = super(CustomSession, self).request(method=method, url=f'{self.base_url}{url}', *args, **kwargs)
        curl = curlify.to_curl(response.request)
        logging.info(f'\n status code: {response.status_code} \n {curl}')
        with step(f'{method} {url} -> status code: {response.status_code}'):
            allure.attach(body=curl, name='Request curl',
                          attachment_type=AttachmentType.TEXT, extension='txt')
            try:
                allure.attach(body=json.dumps(response.json(), ensure_ascii=False, indent=2),
                              name='Response json', attachment_type=allure.attachment_type.JSON, extension=json)
            except requests.exceptions.JSONDecodeError:
                allure.attach(body=response.text, name='Response text', attachment_type=AttachmentType.TEXT,
                              extension='txt')
            return response


reqres_session = CustomSession('https://reqres.in')
