from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    token: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtleSI6InByaXZlZG1lZHZlZCJ9.eyJ1c2VyX2lkIjoiMTExMS0yMjIyLTMzMzMtNDQ0NCIsImV4cGlyZXMiOiIyMDI0LTA1LTMxIDE1OjA2OjM0Iiwicm9sZSI6InRlc3QifQ.immDcieP6IIL3DkrOwCRGnY7hb_yJfc3tZWM8UW6gB4'


test_settings = Settings()
