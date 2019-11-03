import os

import sqlalchemy as db
from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.environ['DATABASE_URL']

Base = declarative_base()
engine = db.create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class Database():
    def __init__(self):
        self.connection = engine.connect()
        print(f"Connected to DB {engine.url.database}")

    def close(self):
        self.closeConnection()

    def closeConnection(self):
        self.connection.close()
        print("DB Instance closed")

    def saveData(self, setting):
        session = Session()        
        session.add(setting)
        session.commit()
        session.close()

    def fetchSetting(self, server_id):
        session = Session()
        settingData = session.query(Setting).filter(Setting.server_id==server_id).first()

        session.close()
        return settingData

    def fetchAllSettings(self):
        session = Session()
        settings = session.query(Setting).all()

        session.close()
        return settings

    def printAllSettings(self):
        session = Session()
        settings = session.query(Setting).all()

        for setting in settings:
            print(setting)
        session.close()

    def updateSetting(self, server_id, motd_channel):
        session = Session()
        dataToUpdate = {Setting.motd_channel: motd_channel}
        settingData = session.query(Setting).filter(Setting.server_id==server_id)
        settingData.update(dataToUpdate)
        session.commit()
        session.close()

    def deleteSetting(self, server_id):
        session = Session()
        settingData = session.query(Setting).filter(Setting.server_id==server_id).first()
        session.delete(settingData)
        session.commit()
        session.close()

class Setting(Base):
    __tablename__ = 'settings'
    server_id = Column(Integer, primary_key=True)
    motd_channel = Column(Integer)
    mcstatus_server = Column(String)

    def __repr__(self): 
        return "<Setting(server_id='%s', motd_channel='%s', mcstatus_server='%s')>" % \
                (self.server_id, self.motd_channel, self.mcstatus_server)

    def __str__(self):
        output = ''
        if self.motd_channel != None:
            output += f'MOTD Channel: {self.motd_channel}\n'
        if self.mcstatus_server != None:
            output += f'Default MC Server Status: {self.mcstatus_server}\n'

        return output
