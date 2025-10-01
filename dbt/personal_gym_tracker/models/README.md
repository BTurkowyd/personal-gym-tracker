# Personal Gym Tracker dbt Project

This dbt project transforms raw workout data from AWS Glue tables into analytical views for tracking fitness progress.

## Project Structure

```
models/
├── staging/          # Cleaned and standardized source data
│   ├── stg_workouts.sql
│   ├── stg_exercises.sql
│   ├── stg_sets.sql
│   └── schema.yml
└── marts/           # Analytical views for business insights
    ├── workout_summary.sql
    ├── exercise_performance.sql
    ├── weekly_summary.sql
    ├── muscle_group_frequency.sql
    └── schema.yml
```

## Data Sources

The project uses three main Glue tables:
- **workouts**: Workout session data
- **performed_exercises**: Exercises performed during workouts
- **sets**: Individual sets for each exercise

## Staging Models

### `stg_workouts`
Cleans and standardizes workout data:
- Converts Unix timestamps to datetime
- Calculates workout duration
- Standardizes column names

### `stg_exercises`
Cleans and standardizes exercise data:
- Standardizes exercise names
- Preserves muscle group and equipment information

### `stg_sets`
Cleans and standardizes set data:
- Calculates set volume (weight × reps)
- Preserves RPE and other metrics

## Mart Models

### `workout_summary`
Comprehensive workout overview with:
- Total exercises, sets, and volume per workout
- Muscle groups trained
- Average RPE and weight statistics

### `exercise_performance`
Exercise-level tracking with:
- Performance progression over time
- Personal best tracking
- Volume and intensity metrics

### `weekly_summary`
Weekly aggregated statistics:
- Workouts per week
- Total training volume
- Total sets and reps
- Average workout duration

### `muscle_group_frequency`
Training frequency analysis:
- Times each muscle group was trained
- Total volume per muscle group
- Days since last training
- Training patterns

## Running the Project

### Compile models
```bash
dbt compile --profiles-dir dbt/personal_gym_tracker
```

### Run all models
```bash
dbt run --profiles-dir dbt/personal_gym_tracker
```

### Run specific models
```bash
dbt run --models staging --profiles-dir dbt/personal_gym_tracker
dbt run --models marts --profiles-dir dbt/personal_gym_tracker
```

### Test models
```bash
dbt test --profiles-dir dbt/personal_gym_tracker
```

### Generate documentation
```bash
dbt docs generate --profiles-dir dbt/personal_gym_tracker
dbt docs serve --profiles-dir dbt/personal_gym_tracker
```

## Use Cases

1. **Track Progress**: Use `exercise_performance` to see if you're improving over time
2. **Analyze Training Volume**: Use `weekly_summary` to ensure consistent training
3. **Balance Training**: Use `muscle_group_frequency` to identify underworked muscle groups
4. **Workout Insights**: Use `workout_summary` to understand workout patterns and intensity

## Configuration

The project is configured to use AWS Athena with the following settings:
- Database: `<aws_account_id>_workouts_database`
- S3 Staging: `s3://<aws_account_id>-workouts-bucket-6mabw3s4smjiozsqyi76rq/dbt`
- Region: `eu-central-1`
- Profile: `cdk-dev`

See `profiles.yml` for full configuration details.
