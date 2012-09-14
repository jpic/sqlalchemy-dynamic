import unittest

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

from alembic.operations import Operations
from alembic.migration import MigrationContext

Base = declarative_base()
engine = sa.create_engine('mysql://root:root@localhost/jpic')
Session = orm.sessionmaker(bind=engine)
session = Session()

conn = engine.connect()
ctx = MigrationContext.configure(conn)
op = Operations(ctx)

for table in ('cars', 'houses', 'persons'):
    op.drop_table(table)


class PersonTest(unittest.TestCase):
    def test_000_create_table(self):

        self.__class__.Person = type('Person', (Base,), {'__tablename__': 'persons',
            'id': sa.Column(sa.Integer, primary_key=True)})

        self.__class__.Car = type('Car', (Base,), {'__tablename__': 'cars',
            'id': sa.Column(sa.Integer, primary_key=True)})

        self.__class__.House = type('House', (Base,), {'__tablename__': 'houses',
            'id': sa.Column(sa.Integer, primary_key=True)})

        Base.metadata.create_all(engine)

    def test_001_create_unicode_field(self):
        # create the column in the table - does not add it in the class
        field = sa.Column('unicode_field', sa.Unicode(50))
        op.add_column('persons', field)

        # create the column in the class - was not done above
        # a new instance to avoid conflicts
        field = sa.Column('unicode_field', sa.Unicode)
        self.__class__.Person.unicode_field = field

        subject = self.__class__.Person(unicode_field='hello unicode field')
        session.add(subject)

        subject = session.query(self.__class__.Person).first()
        self.assertEqual(subject.unicode_field, 'hello unicode field')

    def test_002_create_foreign_key(self):
        field = sa.Column('owner_id', sa.Integer, sa.ForeignKey('persons.id'))
        op.add_column('houses', field)

        # create fk
        op.create_foreign_key('fk_house_owner', 'houses', 'persons', ['owner_id'], ['id'])

        field = sa.Column('owner_id', sa.Integer, sa.ForeignKey('persons.id'))
        relation = orm.relationship('Person',
                backref=orm.backref('houses'))
        self.__class__.House.owner_id = field
        self.__class__.House.owner = relation


        owner = session.query(self.__class__.Person).first()

        house = self.__class__.House()
        house.owner = owner
        session.add(house)

        house = session.query(self.__class__.House).first()

        self.assertEqual(house.owner, owner)
        self.assertEqual(owner.houses, [house])

    def test_003_create_many_to_many(self):
        pass
