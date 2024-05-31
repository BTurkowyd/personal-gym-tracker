import glob
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_tables import Exercise

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
        exercise = Exercise(
            exercise_id=e['id'],
            workout_id=data['id'],
            title=e['title'],
            es_title=e['es_title'],
            de_title=e['de_title'],
            fr_title=e['fr_title'],
            it_title=e['it_title'],
            pt_title=e['pt_title'],
            ko_title=e['ko_title'],
            ja_title=e['ja_title'],
            tr_title=e['tr_title'],
            ru_title=e['ru_title'],
            zh_cn_title=e['zh_cn_title'],
            zh_tw_title=e['zh_tw_title'],
            superset_id=e['superset_id'],
            rest_seconds=e['rest_seconds'],
            notes=e['notes'],
            exercise_template_id=e['exercise_template_id'],
            url=e.get('url', ''),
            exercise_type=e['exercise_type'],
            equipment_category=e['equipment_category'],
            media_type=e.get('media_type', ''),
            custom_exercise_image_url=e['custom_exercise_image_url'],
            custom_exercise_image_thumbnail_url=e['custom_exercise_image_thumbnail_url'],
            muscle_group=e['muscle_group'],
            priority=e['priority'],
        )
        session.add(exercise)

session.commit()