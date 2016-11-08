from handlers.commons import exception_handler
from ieml.usl.tools import usl
from models.usls.usls import USLConnector


# @exception_handler
def save_template(body):
     return {'id': USLConnector().add_template(usl(body.get('ieml')), body.get('paths'),
                                               _tags=body.get('tags', None),
                                               tags_rule=body.get('tags_rules', None),
                                               _keywords=body.get('keywords', None)),
             'success': True}
