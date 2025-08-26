from beanie import Document
from fastapi import UploadFile
# class Document:
#     def __init__(self, title:str, file:UploadFile):
#         self.title = title
#         self.file = file        

class MDocument(Document):
    class Settings: name = "documents"
    
    description: str
    file: str