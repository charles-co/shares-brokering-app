from pydantic import BaseModel


def change_case(value: str, **kwargs) -> str:
    if kwargs["field"].name == "name":
        return value.title()
    return value.upper()


class ErrorSchema(BaseModel):

    detail: str
