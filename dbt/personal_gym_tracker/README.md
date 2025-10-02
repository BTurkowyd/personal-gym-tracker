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

**`personal_records`** - Personal Records (PR) tracking:
- Current PR weight for each exercise
- PR achievement dates and progression
- Total weight improvement and percentage gains
- Number of times PR was broken
- Starting weight vs current PR comparison

**`exercise_frequency`** - Exercise usage and popularity analysis:
- Most and least performed exercises
- Equipment usage patterns
- Exercise distribution and rankings
- Average sets/reps per exercise
- Time since last performance

**`training_patterns`** - Training patterns and consistency:
- Day-of-week training preferences
- Time-of-day workout patterns
- Monthly training trends and statistics
- Consistency metrics and rest day analysis
- Overall training summary statistics

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
5. **Monitor PRs**: Use `personal_records` to track personal bests and strength gains
6. **Exercise Selection**: Use `exercise_frequency` to identify underutilized exercises
7. **Optimize Schedule**: Use `training_patterns` to find best training days and times

## Example Queries

### Find Current PRs for All Exercises
```sql
SELECT exercise_name, current_pr_weight, current_pr_date, improvement_percentage
FROM personal_records
ORDER BY current_pr_weight DESC;
```

### Find Top 10 Most Performed Exercises
```sql
SELECT exercise_name, times_performed, total_volume_kg, avg_rpe
FROM exercise_frequency
WHERE popularity_rank <= 10
ORDER BY popularity_rank;
```

### Analyze Day-of-Week Training Patterns
```sql
SELECT dimension_label as day, metric_count as workouts, metric_avg_duration as avg_duration
FROM training_patterns
WHERE analysis_type = 'day_of_week_analysis'
ORDER BY dimension;
```

### Find Exercises Not Performed Recently
```sql
SELECT exercise_name, last_performed_date, days_since_last_performed
FROM exercise_frequency
WHERE days_since_last_performed > 30
ORDER BY days_since_last_performed DESC;
```

### Monthly Training Summary
```sql
SELECT dimension_label as month, metric_count as workouts, metric_training_days, metric_total_volume
FROM training_patterns
WHERE analysis_type = 'monthly_analysis'
ORDER BY dimension DESC
LIMIT 6;
```

## Extending with New Business Questions

To add new analytical marts:

1. **Create a new SQL file** in `models/marts/` following the existing naming pattern (e.g., `your_mart_name.sql`)
2. **Start with the config block**:
   ```sql
   {{ config(materialized='view') }}
   ```
3. **Reference staging models** using `{{ ref('stg_workouts') }}`, `{{ ref('stg_exercises') }}`, `{{ ref('stg_sets') }}`
4. **Use CTEs** (Common Table Expressions) for readable, modular SQL
5. **Add documentation** to `models/marts/schema.yml`:
   - Model name and description
   - Column descriptions
   - Add tests (not_null, unique, accepted_values, etc.)
6. **Update README.md** with use case and example queries
7. **Run and test** your model:
   ```bash
   dbt run --models your_mart_name --profiles-dir .
   dbt test --models your_mart_name --profiles-dir .
   ```

### Common Patterns

- **Time-based aggregations**: Use `date_trunc('week'|'month', date_column)` for grouping
- **Running totals**: Use window functions with `rows between unbounded preceding and current row`
- **Rankings**: Use `row_number()`, `rank()`, or `dense_rank()` with `over (order by ...)`
- **Lag/Lead**: Use `lag()` or `lead()` for comparing with previous/next records
- **Conditional aggregations**: Use `sum(case when ... then 1 else 0 end)` pattern

## Resources

- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
