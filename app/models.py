import enum
import ormar
import sqlalchemy

from app.database import database


class Status(enum.Enum):
    Speed = "SPEED"
    Stamina = "STAMINA"
    Power = "POWER"
    Guts = "GUTS"
    Wisdom = "WISDOM"


class Aptitude(enum.Enum):
    Turf = "TURF"
    Dirt = "DIRT"
    Short = "SHORT"
    Mile = "MILE"
    Medium = "MEDIUM"
    Long = "LONG"
    Runner = "RUNNER"
    Leader = "LEADER"
    Betweener = "BETWEENER"
    Chaser = "CHASER"


class UmamusumeLocation(enum.Enum):
    Child = "CHILD"
    Parent1 = "PARENT1"
    Parent2 = "PARENT2"


class Star(enum.Enum):
    _1 = 1
    _2 = 2
    _3 = 3


metadata = sqlalchemy.MetaData()


class Friend(ormar.Model):
    class Meta:
        tablename: str = "friend"
        metadata = metadata
        database = database

    friend_code: int = ormar.BigInteger(primary_key=True)
    kakao_id: int = ormar.BigInteger()

    support_kind = ormar.Integer()
    support_level = ormar.Integer()
    comment = ormar.String(max_length=128)


class Umamusume(ormar.Model):
    class Meta:
        tablename = "umamusume"
        metadata = metadata
        database = database

    id: int = ormar.Integer(primary_key=True)
    kind: int = ormar.Integer()

    status_kind: Status = ormar.Enum(enum_class=Status)
    status_star: Star = ormar.Enum(enum_class=Star)

    location: UmamusumeLocation = ormar.Enum(enum_class=UmamusumeLocation)

    aptitude_kind = ormar.Enum(enum_class=Aptitude)
    aptitude_star = ormar.Enum(enum_class=Star)

    unique_skill_kind = ormar.Integer(nullable=True)
    unique_skill_star = ormar.Enum(enum_class=Star, nullable=True)

    owner: Friend = ormar.ForeignKey(Friend)


class TraitInformation(ormar.Model):
    class Meta:
        tablename: str = "trait_information"
        metadata = metadata
        database = database

    trait_id: int = ormar.BigInteger(primary_key=True)
    trait_star: Star = ormar.Enum(enum_class=Star)

    umamusume: Umamusume = ormar.ForeignKey(Umamusume, related_name="trait_informations")
