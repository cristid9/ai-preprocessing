import peewee
import os

BASE_DIR = os.path.dirname(__file__)

database = peewee.SqliteDatabase(os.path.join(BASE_DIR, '..', 'tokens.db'))

class BaseModel(peewee.Model):
    class Meta:
        database = database

class WordStructure(BaseModel):
    text = peewee.CharField(max_length=128)
    pos = peewee.CharField(max_length=32)
    lemma = peewee.CharField(max_length=128)
    case = peewee.CharField(max_length=128)

class PhraseCache(BaseModel):
    phrase = peewee.CharField(max_length=1024)
    md5 = peewee.CharField(max_length=32)
        

if __name__ == '__main__':
    database.create_tables([PhraseCache, WordStructure])


    