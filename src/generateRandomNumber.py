# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/generateRandomNumber.ipynb (unless otherwise specified).

__all__ = ['logger', 'HelperError', 'ParseInputError', 'CheckDatabaseError', 'CreateTableError', 'QueryDatabaseError',
           'USERNUMBERTABLE', 'H', 'EventInput', 'changePassword']

# Cell
import os, logging, sys, requests
import ujson as json
from awsSchema.apigateway import Event,Response
from .NumberTable import NumberTable
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

# Cell
################ Setting Globals from Env Vars ################
USERNUMBERTABLE = os.environ['USERNUMBERTABLE']

# Cell
########## Helper class for main function ##########
EventInput = dict
class H:

    @staticmethod
    @beartype
    def parseInput(event: EventInput) -> str:
        '''
        returns username and password arguments from input
        '''
        body = Event.parseBody(deepcopy(event))
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
    def createTable():
        '''Cretaes the table if it doesn't exist'''

        try:
            if not NumberTable.exists():
                NumberTable.create_table(billing_mode='PAY_PER_REQUEST')
        except Exception as e:
            logger.error(f'Unable to create database:\n{e}')
            raise CreateTableError(f'Unable to create database:\n{e}')

    @staticmethod
    @beartype
    def getNumber(username: str):
        try:
            user = queryResult = NumberTable.query(username)
        except Exception as e:
            logger.error(f'Unable to query database\n{e}')
            raise QueryDatabaseError(f'Unable to query database\n{e}')

        try:
            for U in user:
                return U.number
        except Exception as e:
            logger.error(f"User has no number:\n{e}")
            raise QueryDatabaseError(f"User has no number:\n{e}")



# Cell
############################## Main Function ###############################
def changePassword(event, *args):

  logger.info(f"Number table name :: {USERNUMBERTABLE}")

  evtCpy = deepcopy(event)
  logger.info(f'Event :: {evtCpy}')

  username = H.parseInput(evtCpy)

  if H.usernameInDatabase(username):
    try:
      userNumber = H.getNumber(username)
      output = {'success': True, 'age' : 'old', 'number' : int(userNumber)}
    except Exception as e:
      logger.error(f"Unable to pull number from database:\n{e}")
      output = {'success' : False, 'message' : f'{e}'}
      return Response.returnError(body=output)
    return Response.returnSuccess(body=output)

  URL = 'https://www.random.org/integers/?num=1&min=0&max=10&col=1&base=10&format=plain&rnd=new'
  resp = requests.get(url=URL)

  if resp.status_code == 200:
    try:
      threadItem = NumberTable(username=deepcopy(username), number=json.loads(resp.content))
      threadItem.save()
    except Exception as e:
      logger.error(f'Unable to add user to database\n{e}')
      output = {'success' : False, 'message' : f'e'}
      return Response.returnError(body=output)

    output = {'success' : True, 'age' : 'new', 'number' : json.loads(resp.content)}
    return Response.returnSuccess(body=output)

  output = {'success' : False}
  return Response.returnError("Incorrect Username or Password")