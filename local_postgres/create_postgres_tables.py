from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True)
    username = Column(String)
    profile_image = Column(String)
    verified = Column(Boolean)


class Workout(Base):
    __tablename__ = 'workouts'

    workout_id = Column(String, primary_key=True)
    id = Column(String)
    short_id = Column(String)
    index = Column(Integer)
    start_time = Column(Integer)
    end_time = Column(Integer)
    apple_watch = Column(Boolean)
    wearos_watch = Column(Boolean)
    user_id = Column(String, ForeignKey('users.user_id'))
    nth_workout = Column(Integer)
    like_count = Column(Integer)
    is_liked_by_user = Column(Boolean)
    is_private = Column(Boolean)
    like_images = Column(String)
    comment_count = Column(Integer)
    media = Column(String)
    image_urls = Column(String)
    estimated_volume_kg = Column(Float)


class Exercise(Base):
    __tablename__ = 'exercises'

    exercise_id = Column(String, primary_key=True)
    workout_id = Column(String, ForeignKey('workouts.workout_id'))
    title = Column(String)
    es_title = Column(String)
    de_title = Column(String)
    fr_title = Column(String)
    it_title = Column(String)
    pt_title = Column(String)
    ko_title = Column(String)
    ja_title = Column(String)
    tr_title = Column(String)
    ru_title = Column(String)
    zh_cn_title = Column(String)
    zh_tw_title = Column(String)
    superset_id = Column(String)
    rest_seconds = Column(Integer)
    notes = Column(String)
    exercise_template_id = Column(String)
    url = Column(String)
    exercise_type = Column(String)
    equipment_category = Column(String)
    media_type = Column(String)
    custom_exercise_image_url = Column(String)
    custom_exercise_image_thumbnail_url = Column(String)
    muscle_group = Column(String)
    priority = Column(Integer)


class Set(Base):
    __tablename__ = 'sets'

    set_id = Column(Integer, primary_key=True)
    exercise_id = Column(String, ForeignKey('exercises.exercise_id'))
    index = Column(Integer)
    indicator = Column(String)
    weight_kg = Column(Float)
    reps = Column(Integer)
    distance_meters = Column(Float)
    duration_seconds = Column(Integer)
    rpe = Column(Float)


class PersonalRecord(Base):
    __tablename__ = 'personal_records'

    pr_id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey('sets.set_id'))
    type = Column(String)
    value = Column(Float)


# Create engine and tables
engine = create_engine('postgresql://postgres:password@localhost:5432/postgres')
Base.metadata.create_all(engine)
