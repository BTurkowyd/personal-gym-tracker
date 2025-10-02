# Analytical Marts Guide

This guide provides a comprehensive overview of all analytical marts in the Personal Gym Tracker dbt project and the business questions they answer.


## Overview

The project contains a comprehensive set of analytical marts, each designed to answer specific business questions about workout performance, progression, training patterns, and training quality. The marts below are available in the current dbt project.

## Marts

### 1. workout_summary
**Purpose**: Comprehensive workout overview with aggregated metrics

**Key Metrics**:
- Total exercises, sets, and reps per workout
- Total and average volume (weight × reps)
- Average and maximum weight lifted
- Average RPE (Rate of Perceived Exertion)
- Muscle groups trained
- Workout duration

**Business Questions Answered**:
- What was the composition of each workout?
- Which workouts had the highest training volume?
- What muscle groups are trained together?
- How intense were my workouts (by RPE)?

**Example Query**:
```sql
SELECT workout_date, workout_name, total_exercises, total_volume_kg, avg_rpe
FROM workout_summary
ORDER BY workout_date DESC
LIMIT 10;
```

---

### 2. exercise_performance
**Purpose**: Exercise-level performance tracking with personal bests

**Key Metrics**:
- Performance metrics per exercise per workout
- Personal best weight tracking (historical)
- Total volume, sets, and reps
- Average RPE per exercise
- New PR flags

**Business Questions Answered**:
- Am I improving on specific exercises over time?
- What exercises am I hitting personal records on?
- Which exercises have I plateaued on?
- What's my typical performance for each exercise?

**Example Query**:
```sql
SELECT exercise_name, workout_date, max_weight_kg, personal_best_weight, is_personal_best
FROM exercise_performance
WHERE exercise_name = 'Barbell Squat'
ORDER BY workout_date DESC;
```

---

### 3. weekly_summary
**Purpose**: Weekly aggregated workout statistics

**Key Metrics**:
- Workouts per week
- Total training volume
- Total sets and reps
- Average workout duration
- Week-over-week comparisons

**Business Questions Answered**:
- Am I training consistently week-to-week?
- How has my weekly training volume changed?
- What's my typical weekly workout routine?
- Am I meeting my weekly training goals?

**Example Query**:
```sql
SELECT week_start_date, workouts_per_week, total_volume_kg, total_sets
FROM weekly_summary
ORDER BY week_start_date DESC
LIMIT 12;
```

---

### 4. muscle_group_frequency
**Purpose**: Training frequency analysis by muscle group

**Key Metrics**:
- Times each muscle group was trained
- Total volume per muscle group
- Days since last training
- Average volume per session
- First and last trained dates

**Business Questions Answered**:
- Are my muscle groups balanced?
- Which muscle groups need more attention?
- What's my training frequency for each muscle group?
- How long has it been since I trained a specific muscle group?

**Example Query**:
```sql
SELECT muscle_group, times_trained, total_volume_kg, days_since_last_trained
FROM muscle_group_frequency
ORDER BY times_trained DESC;
```

---

### 5. personal_records
**Purpose**: Comprehensive Personal Records (PR) tracking with progression history

**Key Metrics**:
- Current PR weight for each exercise
- Current PR date and days since PR
- Starting weight and total improvement
- Improvement percentage
- Number of times PR was broken

**Business Questions Answered**:
- What are my current PRs for all exercises?
- How much have I improved on each exercise?
- When did I last set a PR?
- Which exercises have I made the most progress on?
- How many times have I broken PRs?

**Example Query**:
```sql
-- Top 10 exercises by PR weight
SELECT exercise_name, current_pr_weight, current_pr_date, 
       improvement_percentage, pr_count
FROM personal_records
ORDER BY current_pr_weight DESC
LIMIT 10;

-- Exercises with recent PRs (last 30 days)
SELECT exercise_name, current_pr_weight, current_pr_date, days_since_pr
FROM personal_records
WHERE days_since_pr <= 30
ORDER BY current_pr_date DESC;

-- Biggest improvement exercises
SELECT exercise_name, starting_weight, current_pr_weight, 
       total_weight_improvement, improvement_percentage
FROM personal_records
ORDER BY improvement_percentage DESC
LIMIT 10;
```

---

### 6. exercise_frequency
**Purpose**: Exercise usage patterns and popularity analysis

**Key Metrics**:
- Times performed across all workouts
- Days performed
- Total sets, reps, and volume
- Average weight and RPE
- Average sets per performance
- Average reps per set
- Popularity rankings (overall and by muscle group)
- Days since last performed

**Business Questions Answered**:
- What are my most and least performed exercises?
- Which exercises do I neglect?
- What equipment do I use most?
- How is my exercise variety?
- What's the typical rep/set scheme for each exercise?
- Which exercises are most popular in each muscle group?

**Example Query**:
```sql
-- Top 10 most performed exercises
SELECT exercise_name, times_performed, total_volume_kg, popularity_rank
FROM exercise_frequency
ORDER BY popularity_rank
LIMIT 10;

-- Neglected exercises (not performed in 30+ days)
SELECT exercise_name, last_performed_date, days_since_last_performed
FROM exercise_frequency
WHERE days_since_last_performed > 30
ORDER BY days_since_last_performed DESC;

-- Exercise variety by muscle group
SELECT muscle_group, COUNT(*) as exercise_variety
FROM exercise_frequency
GROUP BY muscle_group
ORDER BY exercise_variety DESC;

-- Most popular exercise per muscle group
SELECT exercise_name, muscle_group, times_performed, muscle_group_rank
FROM exercise_frequency
WHERE muscle_group_rank = 1
ORDER BY times_performed DESC;
```

---

### 7. training_patterns
### 8. set_rep_rpe_distribution
**Purpose**: Distribution and percentile analysis for set order, rep count, and RPE

**Key Metrics**:
- Set order distribution (how many sets are performed as first, second, etc.)
- Rep count distribution (how many sets at each rep count)
- RPE (Rate of Perceived Exertion) distribution (how many sets at each RPE)
- RPE percentiles (median, 90th, 95th percentile)

**Business Questions Answered**:
- What is the typical set/rep scheme in my training?
- How hard do I usually train (RPE distribution)?
- What are the most common rep counts?
- What is my typical and peak RPE?

**Example Query**:
```sql
-- Rep count distribution
SELECT col1 as reps, col2 as set_count
FROM set_rep_rpe_distribution
WHERE metric = 'rep_distribution'
ORDER BY CAST(col1 AS INTEGER);

-- RPE percentiles
SELECT col2 as median_rpe, col3 as p90_rpe, col4 as p95_rpe
FROM set_rep_rpe_distribution
WHERE metric = 'rpe_percentiles';
```

---

### 9. monthly_progression
**Purpose**: Best lift and total training volume for each month

**Key Metrics**:
- Best lift (max weight) per month
- Total training volume per month

**Business Questions Answered**:
- How is my strength progressing month-to-month?
- Is my training volume increasing or decreasing over time?

**Example Query**:
```sql
SELECT month, best_lift_kg, total_volume_kg
FROM monthly_progression
ORDER BY month DESC;
```

---

### 10. equipment_usage_trends
**Purpose**: Equipment usage trends by week and month

**Key Metrics**:
- Equipment usage counts by week and month

**Business Questions Answered**:
- What equipment do I use most over time?
- Are there trends in my equipment usage?

**Example Query**:
```sql
SELECT period, equipment_category, period_start, uses
FROM equipment_usage_trends
ORDER BY period_start DESC;
```

---

### 11. movement_pattern_balance
**Purpose**: Estimates push/pull/legs/core balance using exercise name mapping

**Key Metrics**:
- Number of exercises classified as push, pull, legs, core, or other

**Business Questions Answered**:
- Is my training balanced across movement patterns?
- Am I neglecting any movement pattern?

**Example Query**:
```sql
SELECT movement_pattern, exercise_count
FROM movement_pattern_balance
ORDER BY exercise_count DESC;
```

---

### 12. staleness
**Purpose**: Lists exercises and muscle groups not trained in the last N days

**Key Metrics**:
- Days since each exercise or muscle group was last trained

**Business Questions Answered**:
- What exercises or muscle groups am I neglecting?
- How long has it been since I trained a specific exercise?

**Example Query**:
```sql
SELECT exercise_name, muscle_group, last_trained_date, days_since_trained
FROM staleness
ORDER BY days_since_trained DESC;
```

---

### 13. streaks
**Purpose**: Tracks current and longest streaks of consecutive training days

**Key Metrics**:
- Streak start and end dates
- Streak length (number of consecutive days)

**Business Questions Answered**:
- What is my longest training streak?
- What is my current streak?

**Example Query**:
```sql
SELECT streak_start, streak_end, streak_length
FROM streaks
ORDER BY streak_length DESC, streak_end DESC;
```
**Purpose**: Temporal training patterns and consistency analysis

**Key Metrics**:
- Day-of-week workout distribution
- Time-of-day preferences
- Monthly training statistics
- Overall consistency metrics
- Training volume by time period
- Average rest days

**Business Questions Answered**:
- What days of the week do I train most?
- What time of day do I prefer to workout?
- How has my training changed month-to-month?
- Am I training consistently?
- What's my overall training summary?
- Do I train more on weekdays or weekends?

**Example Query**:
```sql
-- Day of week preferences
SELECT dimension_label as day, metric_count as workouts, 
       metric_avg_duration as avg_duration_mins, metric_total_volume
FROM training_patterns
WHERE analysis_type = 'day_of_week_analysis'
ORDER BY dimension;

-- Most common workout hours
SELECT dimension_label as hour, metric_count as workouts
FROM training_patterns
WHERE analysis_type = 'time_of_day_analysis'
ORDER BY metric_count DESC;

-- Monthly training trends (last 6 months)
SELECT dimension_label as month, metric_count as workouts, 
       metric_training_days as days, metric_total_volume
FROM training_patterns
WHERE analysis_type = 'monthly_analysis'
ORDER BY dimension DESC
LIMIT 6;

-- Overall training summary
SELECT dimension_label, metric_count as total_workouts,
       metric_training_days as total_days,
       metric_consistency_pct as consistency
FROM training_patterns
WHERE analysis_type = 'overall_summary';
```

---

## Mart Relationships

```
Source Tables (Glue)
├── workouts
├── performed_exercises
└── sets
    ↓
Staging Models
├── stg_workouts
├── stg_exercises
└── stg_sets
    ↓
Marts (Analytical Views)
├── workout_summary         → Workout-level aggregations
├── exercise_performance    → Exercise progression tracking
├── weekly_summary          → Weekly aggregations
├── muscle_group_frequency  → Muscle group analysis
├── personal_records        → PR tracking and progression
├── exercise_frequency      → Exercise usage patterns
└── training_patterns       → Temporal patterns and consistency
```

## Cross-Mart Analysis Examples

### Find underperforming muscle groups
```sql
-- Muscle groups with low frequency but high recent volume
SELECT 
    mgf.muscle_group,
    mgf.times_trained,
    mgf.days_since_last_trained,
    COUNT(DISTINCT ef.exercise_name) as exercise_variety
FROM muscle_group_frequency mgf
LEFT JOIN exercise_frequency ef ON mgf.muscle_group = ef.muscle_group
GROUP BY mgf.muscle_group, mgf.times_trained, mgf.days_since_last_trained
HAVING mgf.times_trained < 5 OR mgf.days_since_last_trained > 14
ORDER BY mgf.days_since_last_trained DESC;
```

### Training consistency correlation with PRs
```sql
-- See if consistent training correlates with more PRs
SELECT 
    tp.dimension_label as month,
    tp.metric_count as monthly_workouts,
    COUNT(DISTINCT pr.exercise_name) as exercises_with_pr
FROM training_patterns tp
LEFT JOIN personal_records pr 
    ON CAST(YEAR(pr.current_pr_date) AS VARCHAR) || '-' || LPAD(CAST(MONTH(pr.current_pr_date) AS VARCHAR), 2, '0') = tp.dimension
WHERE tp.analysis_type = 'monthly_analysis'
GROUP BY tp.dimension_label, tp.metric_count
ORDER BY tp.dimension_label DESC;
```

### Best training day for PRs
```sql
-- Which day of the week produces the most PRs?
SELECT 
    CASE DAY_OF_WEEK(pr.current_pr_date)
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
        WHEN 7 THEN 'Sunday'
    END as day_name,
    COUNT(*) as pr_count,
    AVG(pr.improvement_percentage) as avg_improvement_pct
FROM personal_records pr
GROUP BY DAY_OF_WEEK(pr.current_pr_date)
ORDER BY pr_count DESC;
```

## Extending the Marts

To add new marts or extend existing ones:

1. **Identify the business question**: What specific question are you trying to answer?
2. **Determine required data**: Which staging models do you need?
3. **Create the mart**: Write SQL in `models/marts/your_mart_name.sql`
4. **Document in schema.yml**: Add model and column descriptions
5. **Add tests**: Create data quality tests in `tests/` directory
6. **Update documentation**: Add to this guide and main READMEs
7. **Test locally**: Run `dbt run --models your_mart_name`

For more details, see the "Extending with New Business Questions" section in the main README.
