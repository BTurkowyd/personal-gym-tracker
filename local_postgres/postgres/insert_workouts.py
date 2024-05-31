import glob
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_tables import Workout

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

    workout = Workout(
        workout_id=data['id'],
        id=data['id'],
        short_id=data['short_id'],
        index=data['index'],
        start_time=format_timestamp(data['start_time']),
        end_time=format_timestamp(data['end_time']),
        apple_watch=data['apple_watch'],
        wearos_watch=data['wearos_watch'],
        user_id=data['user_id'],
        nth_workout=data['nth_workout'],
        like_count=data['like_count'],
        is_liked_by_user=data['is_liked_by_user'],
        is_private=data['is_private'],
        like_images=data['like_images'],
        comment_count=data['comment_count'],
        media=data['media'],
        image_urls=data['image_urls'],
        estimated_volume_kg=data['estimated_volume_kg']
    )
    session.add(workout)

session.commit()
