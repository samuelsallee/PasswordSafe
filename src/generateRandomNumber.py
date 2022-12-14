# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/generateRandomNumber.ipynb (unless otherwise specified).

__all__ = ['logger', 'HelperError', 'ParseInputError', 'CheckDatabaseError', 'CreateTableError', 'QueryDatabaseError',
           'APIError', 'USERNUMBERTABLE', 'H', 'EventInput', 'generateRandomNumber']

# Cell
import os, logging, sys, requests
import ujson as json
from awsSchema.apigateway import Event,Response
from .numberTable import NumberTable
from beartype import beartype
from copy import deepcopy

# Cell
############### Logger for debugging code ##################
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# Cell
###################### Error Definitions ######################
class HelperError(Exception): pass
class ParseInputError(HelperError): pass
class CheckDatabaseError(HelperError): pass
class CreateTableError(HelperError): pass
class QueryDatabaseError(HelperError): pass
class APIError(Exception): pass

# Cell
################ Setting Globals from Env Vars ################
USERNUMBERTABLE = os.environ.get('USERNUMBERTABLE', 'user-number-table-sallee-master')

# Cell
########## Helper class for main function ##########
EventInput = dict
class H:

    randNumUrl = 'https://www.random.org/integers/?num=1&min=0&max=1000&col=1&base=10&format=plain&rnd=new'

    @staticmethod
    @beartype
    def parseInput(event: EventInput) -> str:
        '''
        returns username and password arguments from input
        '''
        body = Event.parseBody(deepcopy(event))
        logger.info(f'Event :: {body}')
        try:
            username = body['username']
        except KeyError:
            logger.error('username is not in body')
            raise ParseInputError('username is not in body')

        return username

    @staticmethod
    @beartype
    def usernameInDatabase(username: str) -> bool:
        try:
            queryResult = NumberTable.query(username)
            listResult = [row for row in queryResult]
            if len(listResult) != 1:
                return False
            return True
        except Exception as e:
            logger.error(f'Unable to check whether or not the username is in the database:\n{e}')
            raise CheckDatabaseError(f'Unable to check whether or not the username is in the database:\n{e}')

    @staticmethod
    @beartype
    def getNumber(username: str):
        try:
            user = queryResult = NumberTable.query(username)
        except Exception as e:
            logger.error(f'Unable to query database\n{e}')
            raise QueryDatabaseError(f'Unable to query database\n{e}')

        try:
            for u in user:
                return u.number
        except Exception as e:
            logger.error(f"User has no number:\n{e}")
            raise QueryDatabaseError(f"User has no number:\n{e}")

# Cell
############################## Main Function ###############################
def generateRandomNumber(event, *args):
    try:
        username = H.parseInput(event)
        if H.usernameInDatabase(username):
            userNumber = H.getNumber(username)
            output = {'success': True, 'age' : 'old', 'number' : int(userNumber)}
            return Response.returnSuccess(body=output)

        resp = requests.get(url=H.randNumUrl)
        if resp.status_code > 399:
            raise APIError(f"{resp.status_code} : {resp.content}")
        threadItem = NumberTable(username=deepcopy(username), number=json.loads(resp.content))
        threadItem.save()
        output = {'success' : True, 'age' : 'new', 'number' : json.loads(resp.content)}
        return Response.returnSuccess(body=output)

    except Exception as e:
        output = {'success' : False}
        return Response.returnError(f"Oops ... Something went wrong {e}", body=output)