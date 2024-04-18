"""Файл класу моделі БД"""

from peewee import *

class Words(Model):
    ID = AutoField()

    Word = CharField(max_length=40)
    Word_Translation = CharField(max_length=100)
    Synonyms = CharField(null=True, default='-')
    Sentences = CharField(null=True)
    Status = CharField(max_length=10, default='not used')
    Level = CharField(null=True)

    def __str__(self):
        return f'{self.Word}'

    def __repr__(self):
        return f'{self.Word}'

    class Meta:
        database = SqliteDatabase('Bot_DB.db')


# class Photos(Model):
#     ID = AutoField()
#
#     Photo_discribtion = CharField(max_length=20)
#     Bynar = BlobField()
#
#     def __str__(self):
#         return f'{self.Photo_discribtion}'
#
#     class Meta:
#         database = SqliteDatabase('Bot_DB.db')

class IrregularVerbs(Model):
    ID = AutoField()

    form_1 = CharField(max_length=40)
    form_2 = CharField(max_length=40)
    form_3 = CharField(max_length=40)
    Translation = CharField(max_length=100)

    def __str__(self):
        return f'{self.form_1}'

    class Meta:
        database = SqliteDatabase('Bot_DB.db')


class UserWords(Model):
    ID = AutoField()

    Word = CharField(max_length=40)
    Word_Translation = CharField(max_length=100)
    UserID = IntegerField()
    Status = CharField(max_length=10, default='not used')

    def __str__(self):
        return (self.Word)

    class Meta:
        database = SqliteDatabase('Bot_DB.db')

# class Settings(Model):
#     UserId = IntegerField()
#     Notification_Freq = IntegerField()
#
#     def __str__(self):
#         return self.__dict__


Words.create_table()
# Photos.create_table()
IrregularVerbs.create_table()
UserWords.create_table()


