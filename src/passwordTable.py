# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/passwordTable.ipynb (unless otherwise specified).

__all__ = ['USERPASSWORDTABLE', 'PasswordTable']

# Cell
import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

# Cell
################ Setting Globals from Env Vars ################
USERPASSWORDTABLE = os.environ.get('USERPASSWORDTABLE', 'user-password-demo-sallee-master')

# Cell
############## Class for accessing DynamoDB #################
class PasswordTable(Model):
    class Meta:
        table_name = USERPASSWORDTABLE
        region = 'ap-southeast-1'

    username = UnicodeAttribute(hash_key=True)
    passwordHash = UnicodeAttribute()
    salt = UnicodeAttribute()
    hashAndSalt = UnicodeAttribute()

