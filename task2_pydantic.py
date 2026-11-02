from pydantic import (BaseModel, 
                      Field, EmailStr,
                      ValidationError,field_validator)
import re

class UserProfile(BaseModel):
    name:str=Field(min_length=2,max_length=50)
    age:int=Field(ge=18,le=100)
    email:EmailStr
    pan:str

    @field_validator('name')
    @classmethod
    def validate_name(cls,value):
        if not value.strip():
            raise ValueError('Name Cannot be Empty')
        return value.strip()

    @field_validator('pan')
    @classmethod
    def validate_pan(cls,value):
        value=value.strip().upper()
        pattren=r"^[A-Z]{5}[0-9]{4}[A-Z]$"

        if not re.fullmatch(pattren,value):
            raise ValueError('INVALID  PAN format')
        return value
try:

    user=UserProfile(
    name='Puneeth',
    age=21,
    email='puneethsai@gmail.com',
    pan='ABCDE1234F'
        )
    print('Valid User Profile')
    print(user.model_dump_json(indent=4))
except ValidationError as e:
    print(e)



try:

    user=UserProfile(
    name='P',
    age=17,
    email='puneethsaigmail.com',
    pan='ABCDEinvalid'
        )
    print('Valid User Profile')
    print(user.model_dump_json(indent=4))
except ValidationError as e:
    for error in e.errors():
        field=error['loc'][0]
        message=error['msg']

        print(f'{field}:{message}')

    