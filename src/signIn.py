# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/signIn.ipynb (unless otherwise specified).

__all__ = ['logger', 'HelperError', 'ParseInputError', 'CheckDatabaseError', 'QueryDatabaseError', 'GetAttributeError',
           'UsernameInTableError', 'WrongHashError', 'USERPASSWORDTABLE', 'H', 'EventInput', 'signIn']

# Cell
########################### Imports ###########################
import hashlib, uuid, os, logging, sys
import ujson as json
from .passwordTable import PasswordTable
from awsSchema.apigateway import Event,Response
from beartype import beartype
from copy import deepcopy
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute

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
class QueryDatabaseError(HelperError): pass
class GetAttributeError(HelperError): pass

class UsernameInTableError(Exception): pass
class WrongHashError(Exception): pass

# Cell
################ Setting Globals from Env Vars ################
USERPASSWORDTABLE = os.environ.get('USERPASSWORDTABLE', 'user-password-demo-sallee-master')

# Cell
########## Helper class for main function ##########
EventInput = dict
class H:
    @staticmethod
    @beartype
    def sha256(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    @beartype
    def salted_sha256(cls, password: str, salt: str ='') -> tuple:
        if salt == '':
            salt = cls.salt()
        return f'{cls.sha256(salt + password)}', f'{salt}'

    @staticmethod
    @beartype
    def parseInput(event: EventInput) -> tuple:
        '''
        returns username and password arguments from input
        '''
        body = Event.parseBody(deepcopy(event))
        logger.info(f'Event :: {event}')
        try:
            username = body.get('username')
        except KeyError:
            logger.error('username is not in body')
            raise ParseInputError('username is not in body')

        try:
            password = body['password']
        except KeyError:
            logger.error('password is not in body')
            raise ParseInputError('password is not in body')

        return username, password

    @staticmethod
    @beartype
    def usernameInDatabase(username: str) -> bool:
        try:
            queryResult = PasswordTable.query(username)
            listResult = [row for row in queryResult]
            if len(listResult) != 1:
                logger.error(f'Username not in table')
                raise UsernameInTableError(f'Username not in table')
                return False
            return True

        except Exception as e:
            logger.error(f'Unable to check whether or not the username is in the database:\n{e}')
            raise CheckDatabaseError(f'Unable to check whether or not the username is in the database:\n{e}')

    @staticmethod
    @beartype
    def tableExists() -> bool:
        try:
            if PasswordTable.exists():
                return True
            return False
        except Exception as e:
            logger.error(f"Unable to see whether or not the database exists:\n{e}")
            raise CheckDatabaseError(f"Unable to see whether or not the database exists:\n{e}")

    @staticmethod
    @beartype
    def getSalt(username: str) -> str:
        try:
            user = queryResult = PasswordTable.query(username)
        except Exception as e:
            logger.error(f'unable to query database:\n{e}')
            raise QueryDatabaseError(f'unable to query database:\n{e}')

        try:
            for u in user:
                logger.info(f"salt :: {u.salt}")
                return u.salt
        except Exception as e:
            logger.error(f"Unable to get the user's hash salt:\n{e}")
            raise GetAttributeError(f"Unable to get the user's hash salt:\n{e}")

    @staticmethod
    @beartype
    def getHash(username: str) -> str:
        try:
            user = queryResult = PasswordTable.query(username)
        except Exception as e:
            logger.error(f'unable to query database:\n{e}')
            raise QueryDatabaseError(f'unable to query database:\n{e}')

        try:
            for u in user:
                logger.info(f'Hash :: {u.passwordHash}')
                return u.passwordHash
        except Exception as e:
            logger.error(f"Unable to get the user's hash salt:\n{e}")
            raise GetAttributeError(f"Unable to get the user's hash salt:\n{e}")


# Cell
##################### Main Function #####################
def signIn(event, *args):
    try:
        if not H.tableExists():
            return Response.returnError("Table doesn't exist")
        username, password = H.parseInput(event)
        H.usernameInDatabase(username)
        salt = H.getSalt(username)
        hash = H.getHash(username)
        hashedPW, salt = H.salted_sha256(password, salt)
        if hashedPW != hash:
            raise WrongHashError(f'Password Hashes do not match')
        return Response.returnSuccess(f"Signed In Successfully")
    except Exception as e:
        return Response.returnError(f"Error :: {e}")
