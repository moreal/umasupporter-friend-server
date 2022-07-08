import typing
import strawberry

from app import models
from app.database import database
from app.dictionary import (
    find_umamusume_image_url,
    find_umamusume_name,
    find_unique_skill_name,
)
from app.models import (
    Star as StarEnum,
    Aptitude as AptitudeEnum,
    Status as StatusEnum,
    UmamusumeLocation,
)

__all__ = ("schema",)

Star = strawberry.enum(StarEnum)
Status = strawberry.enum(StatusEnum)
Aptitude = strawberry.enum(AptitudeEnum)


@strawberry.type
class Trait:
    trait_id: int
    trait_star: Star
    trait_name: str


@strawberry.type
class Umamusume:
    kind: int
    kind_name: str
    status_kind: Status
    status_star: Star
    status_name: str
    aptitude_kind: Aptitude
    aptitude_star: Star
    aptitude_name: str
    unique_skill_kind: int
    unique_skill_star: Star
    unique_skill_name: str
    img: str
    traits: typing.List[Trait]


@strawberry.type
class Friend:
    kakao_id: typing.Optional[int]
    friend_code: int
    support_kind: int
    support_level: int
    comment: str

    umamusume: Umamusume
    parent1: Umamusume
    parent2: Umamusume


@strawberry.input
class StatusFilterInput:
    kind: Status


@strawberry.input
class AptitudeFilterInput:
    kind: Aptitude


@strawberry.input
class UniqueSkillFilterInput:
    kind: int


@strawberry.input
class TraitInput:
    trait_id: int
    trait_star: Star


@strawberry.input
class UmamusumeInput:
    kind: int
    status_kind: Status
    status_star: Star
    aptitude_kind: Aptitude
    aptitude_star: Star
    unique_skill_kind: int
    unique_skill_star: Star
    traits: typing.List[TraitInput]


@strawberry.input
class AddFriendInput:
    friend_code: int
    kakao_id: typing.Optional[int]
    support_kind: int
    support_level: int
    comment: str

    umamusume: UmamusumeInput
    parent1: UmamusumeInput
    parent2: UmamusumeInput


class GraphQLTypeBuilder:

    async def convert_umamusume_model_to_umamusume_type(
        self,
        umamusume: models.Umamusume,
    ) -> Umamusume:
        await umamusume.load()

        return Umamusume(
            kind=umamusume.kind,
            kind_name=find_umamusume_name(umamusume.kind),
            status_kind=umamusume.status_kind,
            status_star=umamusume.status_star,
            status_name=umamusume.status_kind.value,
            aptitude_kind=umamusume.aptitude_kind,
            aptitude_star=umamusume.aptitude_star,
            aptitude_name=umamusume.aptitude_kind.value,
            unique_skill_kind=umamusume.unique_skill_kind,
            unique_skill_star=umamusume.unique_skill_star,
            unique_skill_name=find_unique_skill_name(umamusume.unique_skill_kind),
            img=find_umamusume_image_url(umamusume.kind),
            traits=umamusume.trait_informations,
        )


    async def convert_friend_model_to_friend_type(self, friend: models.Friend) -> Friend:
        await friend.load_all()

        return Friend(
            kakao_id=friend.kakao_id,
            friend_code=friend.friend_code,
            support_kind=friend.support_kind,
            support_level=friend.support_level,
            comment=friend.comment,
            umamusume=await self.convert_umamusume_model_to_umamusume_type(
                next(filter(lambda x: x.location == UmamusumeLocation.Child, friend.umamusumes))
            ),
            parent1=await self.convert_umamusume_model_to_umamusume_type(
                next(filter(lambda x: x.location == UmamusumeLocation.Parent1, friend.umamusumes))
            ),
            parent2=await self.convert_umamusume_model_to_umamusume_type(
                next(filter(lambda x: x.location == UmamusumeLocation.Parent2, friend.umamusumes))
            ),
        )


@strawberry.type
class Query:
    @strawberry.field
    async def friend(self, friend_code: int) -> typing.Optional[Friend]:
        friend = await models.Friend.objects.filter(friend_code=friend_code).get_or_none()
        if friend is None:
            return None

        return await convert_friend_model_to_friend_type(friend=friend)

    @strawberry.field
    async def friends(
        self,
        status_filters: typing.Optional[typing.List[StatusFilterInput]] = None,
        aptitude_filters: typing.Optional[typing.List[AptitudeFilterInput]] = None,
        unique_skill_filters: typing.Optional[typing.List[UniqueSkillFilterInput]] = None,
    ) -> typing.List[Friend]:
        friend_models = await models.Friend.objects.select_all(True).all()
        friends = [await convert_friend_model_to_friend_type(friend) for friend in list(friend_models)]

        if unique_skill_filters is not None:
            for unique_skill_filter in unique_skill_filters:
                friends = list(
                    filter(
                        lambda x: x.umamusume.unique_skill_kind == unique_skill_filter.kind
                        or x.parent1.unique_skill_kind == unique_skill_filter.kind
                        or x.parent2.unique_skill_kind == unique_skill_filter.kind,
                        friends,
                    )
                )
        if status_filters is not None:
            for status_filter in status_filters:
                friends = list(
                    filter(
                        lambda x: x.umamusume.status_kind == status_filter.kind
                        or x.parent1.status_kind == status_filter.kind
                        or x.parent2.status_kind == status_filter.kind,
                        friends,
                    )
                )

        if aptitude_filters is not None:
            for aptitude_filter in aptitude_filters:
                friends = list(
                    filter(
                        lambda x: x.umamusume.aptitude_kind == aptitude_filter.kind
                        or x.parent1.aptitude_kind == aptitude_filter.kind
                        or x.parent2.aptitude_kind == aptitude_filter.kind,
                        friends,
                    )
                )

        return friends


import strawberry.types

@strawberry.type
class Mutation:
    @strawberry.mutation
    @database.transaction()
    async def add_friend(self, input: AddFriendInput) -> Friend:
        friend = await convert_friend_input_to_friend_model(input).save()

        umamusume = build_umamusume_model_from_umamusume_input(input.umamusume, friend, UmamusumeLocation.Child)
        parent1 = build_umamusume_model_from_umamusume_input(input.parent1, friend, UmamusumeLocation.Parent1)
        parent2 = build_umamusume_model_from_umamusume_input(input.parent2, friend, UmamusumeLocation.Parent2)
        await umamusume.save()
        await parent1.save()
        await parent2.save()
        umamusume_and_trait_inputs = [
            (umamusume, input.umamusume.traits),
            (parent1, input.parent1.traits),
            (parent2, input.parent2.traits),
        ]

        for umamusume, trait_inputs in umamusume_and_trait_inputs:
            for trait_input in trait_inputs:
                await convert_trait_input_to_trait_model(trait_input, umamusume=umamusume).save()

        return Friend(
            kakao_id=friend.kakao_id,
            friend_code=friend.friend_code,
            support_kind=friend.support_kind,
            support_level=friend.support_level,
            comment=friend.comment,
            umamusume=await convert_umamusume_model_to_umamusume_type(umamusume),
            parent1=await convert_umamusume_model_to_umamusume_type(parent1),
            parent2=await convert_umamusume_model_to_umamusume_type(parent2),
        )


def build_umamusume_model_from_umamusume_input(
    input: UmamusumeInput, owner: models.Friend, location: UmamusumeLocation
) -> models.Umamusume:
    return models.Umamusume(
        kind=input.kind,
        status_kind=models.Status(input.status_kind),
        status_star=models.Star(input.status_star),
        aptitude_kind=models.Aptitude(input.aptitude_kind),
        aptitude_star=models.Star(input.aptitude_star),
        unique_skill_kind=input.unique_skill_kind,
        unique_skill_star=models.Star(input.unique_skill_star),
        owner=owner,
        location=location,
    )


def convert_friend_input_to_friend_model(input: AddFriendInput) -> models.Friend:
    return models.Friend(
        friend_code=input.friend_code,
        kakao_id=input.kakao_id,
        support_kind=input.support_kind,
        support_level=input.support_level,
        comment=input.comment,
    )


def convert_trait_input_to_trait_model(input: TraitInput, umamusume: models.Umamusume) -> models.TraitInformation:
    return models.TraitInformation(
        trait_id=input.trait_id,
        trait_star=models.Star(input.trait_star),
        umamusume=umamusume.id,
    )


schema = strawberry.Schema(Query, Mutation)
