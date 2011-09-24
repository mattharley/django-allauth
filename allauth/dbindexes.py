from dbindexer.api import register_index
from emailconfirmation.models import EmailAddress

register_index(EmailAddress, {'email': 'iexact', })