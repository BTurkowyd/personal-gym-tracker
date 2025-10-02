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
    ├── personal_records.sql
    ├── exercise_frequency.sql
    ├── training_patterns.sql
    ├── set_rep_rpe_distribution.sql
    ├── monthly_progression.sql
    ├── equipment_usage_trends.sql
    ├── movement_pattern_balance.sql
    ├── staleness.sql
    ├── streaks.sql
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

### `personal_records`
Tracks current PRs for each exercise, PR progression, and improvement metrics.

### `exercise_frequency`
Exercise usage patterns, popularity, and neglect analysis.

### `training_patterns`
Temporal training patterns (day-of-week, time-of-day, monthly, consistency).

### `set_rep_rpe_distribution`
Histograms and percentiles for set order, rep count, and RPE (Rate of Perceived Exertion).

### `monthly_progression`
Best lift and total training volume for each month.

### `equipment_usage_trends`
Equipment usage trends by week and month.

### `movement_pattern_balance`
Estimates push/pull/legs/core balance using exercise name mapping.

### `staleness`
Lists exercises and muscle groups not trained in the last N days.

### `streaks`
Tracks current and longest streaks of consecutive training days.

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
