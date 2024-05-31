import glob
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_tables import Set

load_dotenv('../.env')


def list_files(folder: str) -> list:
    return glob.glob(f'{folder}/*')


def format_timestamp(timestamp: int) -> str:
    dt_object = datetime.utcfromtimestamp(timestamp)
    formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_datetime


engine = create_engine(
    f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@localhost:5432/{os.environ.get("POSTGRES_DB")}')
Session = sessionmaker(bind=engine)
session = Session()

workouts = list_files('./workouts')

for w in workouts:
    with open(w, 'r') as file:
        data = json.load(file)

    for e in data['exercises']:
        for s in e['sets']:
            set_ = Set(
                set_id=s.get('id', ''),
                exercise_id=e.get('id', ''),
                index=s.get('index', ''),
                indicator=s.get('indicator', ''),
                weight_kg=s.get('weight_kg', ''),
                reps=s.get('reps', ''),
                distance_meters=s.get('distance_meters', 0),
                duration_seconds=s.get('diration_seconds', 0),
                rpe=s.get('rpe', ''),
            )
            session.add(set_)

session.commit()

