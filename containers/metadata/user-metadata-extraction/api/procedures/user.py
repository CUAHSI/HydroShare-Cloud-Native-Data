from beanie.odm.operators.update.general import Set

from api.models.user import User


async def create_or_update_user(orcid: str, access_token: str) -> User:
    await User.find_one(User.orcid == orcid).upsert(
        Set({'orcid': orcid, 'access_token': access_token}), on_insert=User(orcid=orcid, access_token=access_token)
    )
    user = await User.find_one(User.access_token == access_token)
    await user.fetch_all_links()
    return user


async def get_user(access_token: str) -> User:
    return await User.find_one(User.access_token == access_token)