import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, Float
from dotenv import load_dotenv

load_dotenv('discord_bot/.env')

password = os.environ.get('DB_PASSWORD')

# Create a PostgreSQL engine
engine = create_engine(f'postgresql://postgres:{password}@3.73.128.85:5432/postgres')

# Create a metadata instance
metadata = MetaData()

# Define tables
users = Table('users', metadata,
              Column('user_id', String, primary_key=True),
              Column('username', String),
              Column('profile_image', String),
              Column('verified', String)
              )

routines = Table('routines', metadata,
                 Column('routine_id', String, primary_key=True),
                 Column('name', String),
                 Column('description', String),
                 Column('created_at', String),
                 Column('updated_at', String),
                 Column('user_id', String, ForeignKey('users.user_id'))
                 )

workouts = Table('workouts', metadata,
                 Column('workout_id', String, primary_key=True),
                 Column('id', String),
                 Column('short_id', String),
                 Column('index', Integer),
                 Column('name', String),
                 Column('description', String),
                 Column('start_time', Integer),
                 Column('end_time', Integer),
                 Column('created_at', String),
                 Column('updated_at', String),
                 Column('routine_id', String, ForeignKey('routines.routine_id'))
                 )

exercises = Table('exercises', metadata,
                  Column('exercise_id', String, primary_key=True),
                  Column('id', String),
                  Column('title', String),
                  Column('es_title', String),
                  Column('de_title', String),
                  Column('fr_title', String),
                  Column('it_title', String),
                  Column('pt_title', String),
                  Column('ko_title', String),
                  Column('ja_title', String),
                  Column('tr_title', String),
                  Column('ru_title', String),
                  Column('zh_cn_title', String),
                  Column('zh_tw_title', String),
                  Column('superset_id', String),
                  Column('rest_seconds', Integer),
                  Column('notes', String),
                  Column('url', String),
                  Column('exercise_type', String),
                  Column('equipment_category', String),
                  Column('media_type', String),
                  Column('custom_exercise_image_url', String),
                  Column('custom_exercise_image_thumbnail_url', String),
                  Column('thumbnail_url', String),
                  Column('muscle_group', String),
                  Column('priority', Integer)
                  )

sets = Table('sets', metadata,
             Column('set_id', Integer, primary_key=True),
             Column('exercise_id', String, ForeignKey('exercises.exercise_id')),
             Column('workout_id', String, ForeignKey('workouts.workout_id')),
             Column('index', Integer),
             Column('indicator', String),
             Column('weight_kg', Float),
             Column('reps', Integer),
             Column('distance_meters', Float),
             Column('duration_seconds', Float),
             Column('rpe', String)
             )

# Create tables in the database
metadata.create_all(engine)
