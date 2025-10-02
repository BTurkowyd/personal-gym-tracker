# Personal Gym Tracker dbt Project

This dbt project transforms raw workout data from AWS Glue tables into analytical views for tracking fitness progress.

## Quick Start

From the repository root:

```bash
# Run all dbt models
make run-dbt

# Or from this directory:
cd dbt/personal_gym_tracker
dbt run --profiles-dir .
```

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

## Models

### Staging Models

**`stg_workouts`** - Cleans and standardizes workout data:
- Converts Unix timestamps to datetime
- Calculates workout duration in minutes
- Rounds volume metrics to 2 decimal places

**`stg_exercises`** - Standardizes exercise data:
- Preserves muscle group and equipment information
- Links to workouts via foreign key

**`stg_sets`** - Processes set data:
- Calculates set volume (weight × reps)
- Rounds all weight and volume metrics to 2 decimal places
- Preserves RPE (Rate of Perceived Exertion)

### Mart Models

**`workout_summary`** - Comprehensive workout overview:
- Total exercises, sets, and volume per workout
- Muscle groups trained
- Average RPE and weight statistics
- Workout duration and timing

**`exercise_performance`** - Exercise progression tracking:
- Performance progression over time
- Personal best detection for each exercise
- Volume and intensity metrics
- Set and rep totals

**`weekly_summary`** - Weekly aggregated statistics:
- Workouts per week
- Total training volume and time
- Average workout duration
- Total sets and reps

**`muscle_group_frequency`** - Training frequency analysis:
- Times each muscle group was trained
- Total volume per muscle group
- Days since last training
- Training patterns and balance

## Running the Project

### From Repository Root
```bash
# Run all models
make run-dbt

# Test models (if tests are defined)
make test-dbt

# Generate documentation
make docs-dbt
```

### From dbt Directory
```bash
cd dbt/personal_gym_tracker

# Compile models
dbt compile --profiles-dir .

# Run all models
dbt run --profiles-dir .

# Run specific models
dbt run --models staging --profiles-dir .
dbt run --models marts --profiles-dir .

# Test models
dbt test --profiles-dir .

# Generate and view documentation
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## Configuration

Configuration is in `profiles.yml`:
- **Database**: `<account_id>_workouts_database`
- **S3 Staging**: `s3://<account_id>-workouts-bucket-6mabw3s4smjiozsqyi76rq/dbt`
- **Region**: `eu-central-1`
- **AWS Profile**: `cdk-dev`

## Use Cases

1. **Track Progress**: Use `exercise_performance` to see if you're improving over time
2. **Analyze Training Volume**: Use `weekly_summary` to ensure consistent training
3. **Balance Training**: Use `muscle_group_frequency` to identify underworked muscle groups
4. **Workout Insights**: Use `workout_summary` to understand workout patterns and intensity

## Resources

- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
