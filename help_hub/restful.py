from fastapi import FastAPI,HTTPException
from sqlalchemy import create_engine,func
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy import Column,Integer,String,DateTime,BINARY,TEXT,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import urllib
from pydantic import BaseModel
import pyodbc

app = FastAPI()
conn = urllib.parse.quote_plus(
    'Data Source Name=MssqlDataSource;'
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=LAPTOP-I39M40T2\SQLEXPRESS;'
    'Database=Students;'
    'Trusted_connection=yes;'
)

try:
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(conn))
    
except:
    print("Failed!")

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()
session = SessionLocal()

class USERSpy(BaseModel):
    ID : int
    USERNAME : String
    PASSWORD:String
    EMAIL:String
    AREA:String
    PHONE:String
    IS_VOLUNTEER:BINARY
    CREATED_AT:DateTime
    UPDATED_AT:DateTime
    class config:
        orm_mode = True

class USERS(Base):
    __tablename__ = "USERS"
    ID = Column(Integer,primary_key=True,index=True)
    USERNAME = Column(String)
    PASSWORD = Column(String)
    EMAIL = Column(String)
    AREA = Column(String)
    PHONE = Column(String)
    IS_VOLUNTEER = Column(BINARY)
    CREATED_AT = Column(DateTime)
    UPDATED_AT = Column(DateTime)

    help_requests = relationship('HelpRequest', back_populates='user')
    volunteer_matches = relationship('VOLUNTEER_MATCH', back_populates='volunteer')
    sent_messages = relationship('ChatMessage', back_populates='sender')


class HelpRequestpy(BaseModel):
    ID:int
    USER_ID :int
    REQUEST_TYPE:String
    DESCRIPTION:TEXT
    STATUS:String
    AREA:String
    CREATED_AT:DateTime
    IS_FINISHED:BINARY
    UPDATED_AT:DateTime
    class config:
        orm_mode = True

class HelpRequest(Base):
    __tablename__ = "HelpRequest"
    ID = Column(Integer,primary_key=True,index=True)
    USER_ID = Column(Integer,ForeignKey('USERS.ID'))
    REQUEST_TYPE = Column(String)
    DESCRIPTION = Column(String)
    STATUS = Column(String)
    AREA = Column(String)
    CREATED_AT = Column(DateTime)
    IS_FINISHED = Column(BINARY)
    UPDATED_AT = Column(DateTime)

    user = relationship('USER', back_populates='help_requests')
    volunteer_matches = relationship('VOLUNTEER_MATCH', back_populates='help_request')
    chat_messages = relationship('Chat_MESSAGE_TABLE', back_populates='help_request')


class VOLUNTEER_MATCHpy(BaseModel):
    ID:int
    HELP_REQUEST_ID :int
    VOLUNTEER_USER_ID:int
    STATUS:String
    CREATED_AT: DateTime
    UPDATED_AT:DateTime
    class config:
        orm_mode = True

class VOLUNTEER_MATCH(Base):
    __tablename__="VOLUNTEER_MATCH"
    ID = Column(Integer,primary_key=True,index=True)
    HELP_REQUEST_ID = Column(Integer,ForeignKey('HelpRequest.ID'))
    VOLUNTEERS_USER_ID = Column(Integer,ForeignKey('USERS.ID'))
    STATUS = Column(String)
    CREATED_AT = Column(DateTime)
    UPDATED_AT = Column(DateTime)

    help_request = relationship('HelpRequest', back_populates='volunteer_matches')
    volunteer = relationship('USER', back_populates='volunteer_matches')


class CHAT_MESSAGE_TABLEpy(BaseModel):
    ID:int
    SENDER_USER_ID:int
    HELP_REQUEST_ID:int
    MESSAGE:String
    TIMESTAMP:DateTime
    class config:
        orm_mode = True

class CHAT_MESSAGE_TABLE(Base):
    __tablename__="CHAT_MESSAGE_TABLE"
    ID = Column(Integer,primary_key=True,index=True)
    SENDER_USER_ID = Column(Integer,ForeignKey('USERS.ID'))
    HELP_REQUEST_ID = Column(Integer,ForeignKey('USERS.ID'))
    MESSAGE = Column(String)
    TIMESTAMP = Column(DateTime)

    help_request = relationship('HelpRequest', back_populates='chat_messages')
    sender = relationship('User', back_populates='sent_messages')


@app.post("/users/", response_model=USERSpy)
def create_user(user: USERSpy):
    new_user = USERS()
    new_user.USERNAME = user.USERNAME
    new_user.PASSWORD = user.PASSWORD
    new_user.EMAIL = user.EMAIL
    new_user.AREA = user.AREA
    new_user.PHONE = user.PHONE
    new_user.IS_VOLUNTEER = user.IS_VOLUNTEER
    new_user.CREATED_AT = user.CREATED_AT
    new_user.UPDATED_AT = user.UPDATED_AT
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    user1 = USERSpy.from_orm(new_user)
    user1 = user1.json()
    return user1

@app.get("user/info/{user_id}")
def read_user(user_id:int):
    find_user = session.query(USERS).filter(USERS.ID==user_id).first();
    find_user = find_user.json()
    return find_user

@app.put("/users/update_info/{user_id}", response_model=USERSpy)
def update_user(user_id: int, updated_user: USERSpy):
    if(user_id<session.query(func.count(USERS.ID)).scalar()):
        find_user = session.query(USERS).filter(USERS.ID==user_id).first();
        find_user.ID = updated_user.ID
        find_user.USERNAME = updated_user.USERNAME
        find_user.PASSWORD = updated_user.PASSWORD
        find_user.EMAIL = updated_user.EMAIL
        find_user.AREA = updated_user.AREA
        find_user.PHONE = updated_user.PHONE
        find_user.IS_VOLUNTEER = updated_user.IS_VOLUNTEER
        find_user.CREATED_AT = updated_user.CREATED_AT
        find_user.UPDATED_AT = updated_user.UPDATED_AT
        session.commit()
        session.refresh(find_user)
        user1 = USERSpy.from_orm(find_user)
        user1 = user1.json()
        return user1
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/Delete_Profile/{user_id}", response_model=USERSpy)
def delete_user(user_id: int):
    find_user = session.query(USERS).filter(USERS.ID==user_id).first();
    session.delete(find_user)
    session.commit()
    return find_user

@app.post("/help-requests/", response_model=HelpRequestpy)
def create_help_request(request: HelpRequestpy):
    new_request = HelpRequest()
    new_request.USER_ID = request.USER_ID
    new_request.REQUEST_TYPE = request.REQUEST_TYPE
    new_request.DESCRIPTION = request.DESCRIPTION
    new_request.STATUS=request.STATUS
    new_request.AREA = request.AREA
    new_request.CREATED_AT=request.CREATED_AT
    new_request.IS_FINISHED= request.IS_FINISHED
    new_request.UPDATED_AT=request.UPDATED_AT
    session.add(new_request)
    session.commit()
    session.refresh(new_request)
    request1 = USERSpy.from_orm(request1)
    request1 = request1.json()
    return request1

@app.get("/help-requests/{request_id}", response_model=HelpRequestpy)
def read_help_request(request_id: int):
    find_request = session.query(HelpRequest).filter(HelpRequest.ID == request_id).first();
    find_request = find_request.json()
    return find_request

@app.put("/help-requests/{request_id}", response_model=HelpRequestpy)
def update_help_request(request_id: int, updated_request: HelpRequestpy):
    if(request_id<session.query(func.count(HelpRequest.ID))):

        find_request = session.query(HelpRequest).filter(HelpRequest.ID==request_id).first();
        find_request.USER_ID = updated_request.USER_ID
        find_request.REQUEST_TYPE=updated_request.REQUEST_TYPE
        find_request.DESCRIPTION=updated_request.DESCRIPTION
        find_request.STATUS=updated_request.STATUS
        find_request.AREA=updated_request.AREA
        find_request.CREATED_AT=updated_request.CREATED_AT
        find_request.IS_FINISHED=updated_request.IS_FINISHED
        find_request.UPDATED_AT=updated_request.UPDATED_AT
        session.commit()
        session.refresh(find_request)
        request1 = HelpRequestpy.from_orm(find_request)
        request1 = request1.json()
        return request1
    else:
        raise HTTPException(status_code=404, detail="request not found")

@app.delete("/help-requests/{request_id}", response_model=HelpRequestpy)
def delete_help_request(request_id: int):
    if request_id < session.query(func.count(HelpRequest.ID)):
        deleted_request = session.query(HelpRequest).filter(HelpRequest.ID==request_id)
        session.delete(deleted_request)
        session.commit()
        return deleted_request
    raise HTTPException(status_code=404, detail="Help request not found")  

@app.post("/volunteer-matches/", response_model=VOLUNTEER_MATCHpy)
def create_volunteer_match(match: VOLUNTEER_MATCHpy):
    new_match = VOLUNTEER_MATCH()
    new_match.HELP_REQUEST_ID = match.HELP_REQUEST_ID
    new_match.VOLUNTEER_USER_ID = match.VOLUNTEER_USER_ID
    new_match.STATUS = match.STATUS
    new_match.CREATED_AT = match.CREATED_AT
    new_match.UPDATED_AT = match.UPDATED_AT
    session.add(new_match)
    session.commit()
    session.refresh(new_match)
    match1 = VOLUNTEER_MATCHpy.from_orm(new_match)
    return match1

@app.get("/volunteer-matches/{match_id}", response_model=VOLUNTEER_MATCHpy)
def read_volunteer_match(match_id: int):
    find_match = session.query(VOLUNTEER_MATCH).filter(VOLUNTEER_MATCH.ID == match_id).first()
    if find_match:
        match = VOLUNTEER_MATCHpy.from_orm(find_match)
        return match
    raise HTTPException(status_code=404, detail="Volunteer match not found")

@app.put("/volunteer-matches/{match_id}", response_model=VOLUNTEER_MATCHpy)
def update_volunteer_match(match_id: int, updated_match: VOLUNTEER_MATCHpy):
    find_match = session.query(VOLUNTEER_MATCH).filter(VOLUNTEER_MATCH.ID == match_id).first()
    if find_match:
        find_match.HELP_REQUEST_ID = updated_match.HELP_REQUEST_ID
        find_match.VOLUNTEER_USER_ID = updated_match.VOLUNTEER_USER_ID
        find_match.STATUS = updated_match.STATUS
        find_match.UPDATED_AT = updated_match.UPDATED_AT
        session.commit()
        session.refresh(find_match)
        match = VOLUNTEER_MATCHpy.from_orm(find_match)
        return match
    raise HTTPException(status_code=404, detail="Volunteer match not found")

@app.delete("/volunteer-matches/{match_id}", response_model=VOLUNTEER_MATCHpy)
def delete_volunteer_match(match_id: int):
    find_match = session.query(VOLUNTEER_MATCH).filter(VOLUNTEER_MATCH.ID == match_id).first()
    if find_match:
        session.delete(find_match)
        session.commit()
        match = VOLUNTEER_MATCHpy.from_orm(find_match)
        return match
    raise HTTPException(status_code=404, detail="Volunteer match not found")