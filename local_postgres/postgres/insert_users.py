from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from dotenv import load_dotenv
import os
from create_tables import User

load_dotenv('../.env')

engine = create_engine(f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@localhost:5432/{os.environ.get("POSTGRES_DB")}')
Session = sessionmaker(bind=engine)
session = Session()

user = User(
    user_id='f0ef678d-56e1-42c1-81ec-b9f2eda7f657',
    username='vertislav',
    profile_image='https://d2l9nsnmtah87f.cloudfront.net/profile-images/vertislav-2bc7c904-634c-4063-ac6c-458022a4a36e.jpg',
    verified=False
)
session.add(user)
session.commit()