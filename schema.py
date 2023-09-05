import typing

import pydantic


class CreateAds(pydantic.BaseModel):
    title: str
    description: str
    owner: str

    @pydantic.validator("title")
    def title_length(cls, value):
        if 1 > len(value) > 50:
            raise ValueError("inappropriate title length")
        return value


class UpdateAds(pydantic.BaseModel):
    title: str
    description: str
    owner: str

    @pydantic.validator("title")
    def title_length(cls, value):
        if 1 > len(value) > 50:
            raise ValueError("inappropriate title length")
        return value
