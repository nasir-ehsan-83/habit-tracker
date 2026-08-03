from pydantic import (
    BaseModel, 
    EmailStr
)



class VerifyEmail(BaseModel):
    email:         EmailStr
    verify_code:   int



class ResetPassword(BaseModel):
    email:          EmailStr
    new_password:       str
    verify_token:   str