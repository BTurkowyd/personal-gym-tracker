import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_postgres_tables import User, Routine, Workout, Exercise, Set, PersonalRecord  # Import your SQLAlchemy models

# Read JSON file
with open('/Users/bartoszturkowyd/Projects/aws/silka/local_testing/E952F27A-F613-40C8-A776-4858C1656DD9.json', 'r') as f:
    data = json.load(f)

# Create engine and session
engine = create_engine('postgresql://postgres:password@localhost:5432/postgres')
Session = sessionmaker(bind=engine)
session = Session()

# Define function to convert JSON data to SQLAlchemy objects and commit to database
def commit_to_database(data):
    # Extract data
    routine_data = data.get('routine_data', {})
    workout_data = data.get('workout_data', {})
    exercises_data = data.get('exercises_data', {})

    # Add user to database
    user = User(
        user_id=data['user_id'],
        username=data['username'],
        profile_image=data['profile_image'],
        verified=data['verified']
    )
    session.add(user)

    # Add routine to database
    routine = Routine(
        routine_id=data['routine_id'],
        name=data['name'],
        description=data['description'],
        created_at=data['created_at'],
        updated_at=data['updated_at'],
        user_id=data['user_id']
    )
    session.add(routine)

    # Add workout to database
    workout = Workout(
        workout_id=data['id'],
        id=data['id'],
        short_id=data['short_id'],
        index=data['index'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        routine_id=data['routine_id'],
        apple_watch=data['apple_watch'],
        wearos_watch=data['wearos_watch'],
        user_id=data['user_id'],
        nth_workout=data['nth_workout'],
        like_count=data['like_count'],
        is_liked_by_user=data['is_liked_by_user'],
        is_private=data['is_private'],
        like_images=json.dumps(data['like_images']),  # Convert to string
        comment_count=data['comment_count'],
        media=json.dumps(data['media']),  # Convert to string
        image_urls=json.dumps(data['image_urls']),  # Convert to string
        estimated_volume_kg=data['estimated_volume_kg']
    )
    session.add(workout)

    # Add exercises and sets to database
    for exercise_data in exercises_data:
        exercise = Exercise(
            exercise_id=exercise_data['exercise_id'],
            workout_id=workout_data['workout_id'],
            title=exercise_data['title'],
            es_title=exercise_data['es_title'],
            de_title=exercise_data['de_title'],
            fr_title=exercise_data['fr_title'],
            it_title=exercise_data['it_title'],
            pt_title=exercise_data['pt_title'],
            ko_title=exercise_data['ko_title'],
            ja_title=exercise_data['ja_title'],
            tr_title=exercise_data['tr_title'],
            ru_title=exercise_data['ru_title'],
            zh_cn_title=exercise_data['zh_cn_title'],
            zh_tw_title=exercise_data['zh_tw_title'],
            superset_id=exercise_data['superset_id'],
            rest_seconds=exercise_data['rest_seconds'],
            notes=exercise_data['notes'],
            exercise_template_id=exercise_data['exercise_template_id'],
            url=exercise_data['url'],
            exercise_type=exercise_data['exercise_type'],
            equipment_category=exercise_data['equipment_category'],
            media_type=exercise_data['media_type'],
            custom_exercise_image_url=exercise_data['custom_exercise_image_url'],
            custom_exercise_image_thumbnail_url=exercise_data['custom_exercise_image_thumbnail_url'],
            muscle_group=exercise_data['muscle_group'],
            priority=exercise_data['priority']
        )
        session.add(exercise)

        for set_data in exercise_data['sets']:
            set_ = Set(
                exercise_id=exercise_data['exercise_id'],
                index=set_data['index'],
                indicator=set_data['indicator'],
                weight_kg=set_data['weight_kg'],
                reps=set_data['reps'],
                distance_meters=set_data['distance_meters'],
                duration_seconds=set_data['duration_seconds'],
                rpe=set_data['rpe']
            )
            session.add(set_)

            for pr_data in set_data['prs']:
                pr = PersonalRecord(
                    set_id=set_data['id'],
                    type=pr_data['type'],
                    value=pr_data['value']
                )
                session.add(pr)

    # Commit changes
    session.commit()

# Call the function with your JSON data
commit_to_database(data)
