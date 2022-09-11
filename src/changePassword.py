# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/changePassword.ipynb (unless otherwise specified).

__all__ = ['logger', 'HelperError', 'ParseInputError', 'CheckDatabaseError', 'QueryDatabaseError', 'GetAttributeError',
           'NewPasswordError', 'USERPASSWORDTABLE', 'Thread', 'H', 'EventInput', 'changePassword']

# Cell
########################### Imports ###########################
import hashlib, uuid, os, logging, sys
import ujson as json
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
class NewPasswordError(HelperError): pass

# Cell
################ Setting Globals from Env Vars ################
USERPASSWORDTABLE = os.environ['USERPASSWORDTABLE']

# Cell
############## Class for accessing DynamoDB #################
class Thread(Model):
    class Meta:
        table_name = USERPASSWORDTABLE
        region = 'ap-southeast-1'

    username = UnicodeAttribute(hash_key=True, attr_name='username')
    passwordHash = UnicodeAttribute(range_key=True, attr_name='passwordHash')
    salt = UnicodeAttribute(attr_name='salt')
    hashAndSalt = UnicodeAttribute(attr_name='hashAndSalt')

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
        try:
            username = body['username']
        except KeyError:
            logger.error('username is not in body')
            raise ParseInputError('username is not in body')

        try:
            oldPassword = body['oldPassword']
        except KeyError:
            logger.error('oldPassword is not in body')
            raise ParseInputError('oldPassword is not in body')

        try:
            newPassword = body['newPassword']
        except KeyError:
            logger.error('newPassword is not in body')
            raise ParseInputError('newPassword is not in body')


        return username, oldPassword, newPassword

    @staticmethod
    @beartype
    def usernameInDatabase(username: str) -> bool:
        try:
            queryResult = Thread.query(username)
            listResult = [row for row in queryResult]
            if len(listResult) != 1:
                return False
            return True
        except Exception as e:
            logger.error(f'Unable to check whether or not the username is in the database:\n{e}')
            raise CheckDatabaseError(f'Unable to check whether or not the username is in the database:\n{e}')

    @staticmethod
    @beartype
    def tableExists() -> bool:
        try:
            if Thread.exists():
                return True
            return False
        except Exception as e:
            logger.error(f"Unable to see whether or not the database exists:\n{e}")
            raise CheckDatabaseError(f"Unable to see whether or not the database exists:\n{e}")

    @staticmethod
    @beartype
    def getSalt(username: str) -> str:
        try:
            user = queryResult = Thread.query(username)
        except Exception as e:
            logger.error(f'unable to query database:\n{e}')
            raise QueryDatabaseError(f'unable to query database:\n{e}')

        try:
            for U in user:
                return U.salt
        except Exception as e:
            logger.error(f"Unable to get the user's hash salt:\n{e}")
            raise GetAttributeError(f"Unable to get the user's hash salt:\n{e}")

    @staticmethod
    @beartype
    def getHash(username: str) -> str:
        try:
            user = queryResult = Thread.query(username)
        except Exception as e:
            logger.error(f'unable to query database:\n{e}')
            raise QueryDatabaseError(f'unable to query database:\n{e}')

        try:
            for U in user:
                return U.passwordHash
        except Exception as e:
            logger.error(f"Unable to get the user's hash salt:\n{e}")
            raise GetAttributeError(f"Unable to get the user's hash salt:\n{e}")

    @staticmethod
    @beartype
    def setNewPassword(username: str, hash: str, salt: str, hashAndSalt: str):
        try:
            try:
                logger.info(f'username :: {username}')
                user = Thread.get(username)
            except Exception as e:
                logger.error(f"Unable to perform get function ::\n{e}")
                raise Exception(f"Unable to perform get function ::\n{e}")

            logger.info(f'user :: {user}')
            user.update(actions=[
                Thread.passwordHash.set(hash),
                Thread.hashAndSalt.set(hashAndSalt),
                Thread.salt.set(salt)
            ])
        except Exception as e:
            logger.error(f'Unable to add user to the database:\n{e}')
            raise NewPasswordError(f'Unable to add user to the database:\n{e}')

    @staticmethod
    @beartype
    def salt() -> str:
        return uuid.uuid4().hex


# Cell
############################## Main Function ###############################
def changePassword(event, *args):

  logger.info(f"Password table name :: {USERPASSWORDTABLE}")

  evtCpy = deepcopy(event)
  logger.info(f'Event :: {evtCpy}')

  username, oldPassword, newPassword = H.parseInput(evtCpy)
  # Take this away before using, it isn't a good idea to save the username and pw in logs
  # logger.info(f"Username :: {username}\npassword :: {password}")

  if H.usernameInDatabase(username):
    oldSalt = H.getSalt(username)
    oldHash = H.getHash(username)
    logger.info(f"Old Hash :: {oldHash}")
    logger.info(f"Old Salt :: {oldSalt}")
    hashedPW, salt = H.salted_sha256(oldPassword, oldSalt)
    if hashedPW == oldHash:

      newHash, newSalt = H.salted_sha256(newPassword)
      newHashAndSalt = newHash + ':' + newSalt
      logger.info(f'new Hash :: {newHash}')
      logger.info(f'new Salt :: {newSalt}')

      H.setNewPassword(username, newHash, newSalt, newHashAndSalt)
      return Response.returnSuccess("Password Changed Successfully")
    return Response.returnError("Incorrect Username or Password")

  return Response.returnError("Invalid Username")