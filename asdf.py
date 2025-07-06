import json
import csv

workout_json = """
{
  "id": "CA3DCA00-D593-4258-B4C8-FDAB3B373A50",
  "name": "Legs/glutes workout",
  "index": 95390094,
  "media": [],
  "user_id": "f0ef678d-56e1-42c1-81ec-b9f2eda7f657",
  "comments": [],
  "end_time": 1737481427,
  "short_id": "26xMRLMUuwx",
  "username": "vertislav",
  "verified": false,
  "exercises": [
    {
      "id": "c3635c25-45db-4d9c-8b9a-417a5c9dddb5",
      "url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-assets/07391201-Sled-45-Leg-Press_Hips.mp4",
      "sets": [
        {
          "id": "2043521837",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 0,
          "indicator": "normal",
          "weight_kg": 183,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521838",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 1,
          "indicator": "normal",
          "weight_kg": 183,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521839",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 2,
          "indicator": "normal",
          "weight_kg": 183,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        }
      ],
      "notes": "",
      "title": "Leg Press (Machine)",
      "de_title": "Beinpresse ",
      "es_title": "Press de Piernas",
      "fr_title": "Presse à Cuisses",
      "it_title": "Leg Press (Macchina)",
      "ja_title": "レッグプレス　（マシン）",
      "ko_title": "레그 프레스 (머신)",
      "priority": 9,
      "pt_title": "Leg Press 45º (Máquina)",
      "ru_title": "Жим ногами (Тренажёр)",
      "tr_title": "Leg Press (Makine)",
      "media_type": "video",
      "superset_id": null,
      "zh_cn_title": "腿举（机）",
      "zh_tw_title": "腿舉（機）",
      "muscle_group": "quadriceps",
      "rest_seconds": 180,
      "exercise_type": "weight_reps",
      "other_muscles": [],
      "thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/07391201-Sled-45-Leg-Press_Hips_thumbnail@3x.jpg",
      "equipment_category": "machine",
      "exercise_template_id": "C7973E0E",
      "volume_doubling_enabled": false,
      "custom_exercise_image_url": null,
      "custom_exercise_image_thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/07391201-Sled-45-Leg-Press_Hips_thumbnail@3x.jpg"
    },
    {
      "id": "59560104-7e3a-408f-a948-d4fc94ea2468",
      "url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-assets/05941201-Lever-Seated-Calf-Raise-(plate-loaded).mp4",
      "sets": [
        {
          "id": "2043521840",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 0,
          "indicator": "normal",
          "weight_kg": 52.5,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521841",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 1,
          "indicator": "normal",
          "weight_kg": 57.5,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521842",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 2,
          "indicator": "normal",
          "weight_kg": 57.5,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        }
      ],
      "notes": "",
      "title": "Seated Calf Raise",
      "de_title": "Wadenheben sitzend",
      "es_title": "Elevación de Gemelos Sentado",
      "fr_title": "Extension Mollets Assis",
      "it_title": "Calf Raise Seduto",
      "ja_title": "シーテッドカーフレイズ",
      "ko_title": "시티드 카프 레이즈",
      "priority": 8,
      "pt_title": "Elevação de Panturrilha Sentado (Máquina)",
      "ru_title": "Подъем на носки сидя",
      "tr_title": "Oturarak Calf Raise",
      "media_type": "video",
      "superset_id": null,
      "zh_cn_title": "坐姿提踵",
      "zh_tw_title": "坐姿提踵",
      "muscle_group": "calves",
      "rest_seconds": 120,
      "exercise_type": "weight_reps",
      "other_muscles": [],
      "thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/05941201-Lever-Seated-Calf-Raise-(plate-loaded)_thumbnail@3x.jpg",
      "equipment_category": "machine",
      "exercise_template_id": "062AB91A",
      "volume_doubling_enabled": false,
      "custom_exercise_image_url": null,
      "custom_exercise_image_thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/05941201-Lever-Seated-Calf-Raise-(plate-loaded)_thumbnail@3x.jpg"
    },
    {
      "id": "71092d25-4317-4a01-a763-e4e9178b25f6",
      "url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-assets/05851201-Lever-Leg-Extension_Thighs.mp4",
      "sets": [
        {
          "id": "2043521843",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 0,
          "indicator": "normal",
          "weight_kg": 69,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521844",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 1,
          "indicator": "normal",
          "weight_kg": 69,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521845",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 2,
          "indicator": "normal",
          "weight_kg": 69,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        }
      ],
      "notes": "",
      "title": "Leg Extension (Machine)",
      "de_title": "Beinstrecken ",
      "es_title": "Extensión de Pierna",
      "fr_title": "Extension Jambes",
      "it_title": "Leg Extension (Macchina)",
      "ja_title": "レッグエクステンション　（マシン）",
      "ko_title": "레그 익스텐션 (머신)",
      "priority": 10,
      "pt_title": "Cadeira Extensora (Máquina)",
      "ru_title": "Разгибание ног (Тренажёр)",
      "tr_title": "Leg Extension (Makine)",
      "media_type": "video",
      "superset_id": null,
      "zh_cn_title": "腿部伸展（机器）",
      "zh_tw_title": "腿部伸展（機器）",
      "muscle_group": "quadriceps",
      "rest_seconds": 150,
      "exercise_type": "weight_reps",
      "other_muscles": [],
      "thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/05851201-Lever-Leg-Extension_Thighs_thumbnail@3x.jpg",
      "equipment_category": "machine",
      "exercise_template_id": "75A4F6C4",
      "volume_doubling_enabled": false,
      "custom_exercise_image_url": null,
      "custom_exercise_image_thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/05851201-Lever-Leg-Extension_Thighs_thumbnail@3x.jpg"
    },
    {
      "id": "67b0f0e2-529f-4967-ad9e-f80ba282f863",
      "url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-assets/05981201-Lever-Seated-Hip-Adduction_Thighs.mp4",
      "sets": [
        {
          "id": "2043521846",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 0,
          "indicator": "normal",
          "weight_kg": 91,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521847",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 1,
          "indicator": "normal",
          "weight_kg": 95,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521848",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 2,
          "indicator": "normal",
          "weight_kg": 98.5,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        }
      ],
      "notes": "",
      "title": "Hip Adduction (Machine)",
      "de_title": "Hüftadduktion",
      "es_title": "Aducción de Caderas",
      "fr_title": "Adduction Hanche",
      "it_title": "Adduzione Anche (Macchina)",
      "ja_title": "ヒップアブダクション（マシン）",
      "ko_title": "힙 어덕션 (머신)",
      "priority": 0,
      "pt_title": "Cadeira Adutora (Máquina)",
      "ru_title": "Сведение бедра (Тренажёр)",
      "tr_title": "Hip Adduction (Makine)",
      "media_type": "video",
      "superset_id": null,
      "zh_cn_title": "髋关节内收（机器）",
      "zh_tw_title": "髖關節內收（機器）",
      "muscle_group": "adductors",
      "rest_seconds": 120,
      "exercise_type": "weight_reps",
      "other_muscles": [],
      "thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/05981201-Lever-Seated-Hip-Adduction_Thighs_thumbnail@3x.jpg",
      "equipment_category": "machine",
      "exercise_template_id": "8BEBFED6",
      "volume_doubling_enabled": false,
      "custom_exercise_image_url": null,
      "custom_exercise_image_thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/05981201-Lever-Seated-Hip-Adduction_Thighs_thumbnail@3x.jpg"
    },
    {
      "id": "70492f73-35d1-4926-b806-4834aa568805",
      "url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-assets/05861201-Lever-Lying-Leg-Curl_Thighs.mp4",
      "sets": [
        {
          "id": "2043521849",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 0,
          "indicator": "normal",
          "weight_kg": 53.5,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521850",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 1,
          "indicator": "normal",
          "weight_kg": 54,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        },
        {
          "id": "2043521851",
          "prs": [],
          "rpe": null,
          "reps": 10,
          "index": 2,
          "indicator": "normal",
          "weight_kg": 54,
          "distance_meters": 0,
          "personalRecords": [],
          "duration_seconds": 0
        }
      ],
      "notes": "",
      "title": "Lying Leg Curl (Machine)",
      "de_title": "Liegendes Beinbeugen (Maschine)",
      "es_title": "Curl de Piernas Acostado (Máquina)",
      "fr_title": "Leg Curl Allongé (Machine)",
      "it_title": "Leg Curl Sdraiato (Macchina)",
      "ja_title": "シーテッドレッグカール　（マシン）",
      "ko_title": "라잉 레그 컬 (머신)",
      "priority": 10,
      "pt_title": "Mesa Flexora (Máquina)",
      "ru_title": "Сгибание ног лежа (Тренажёр)",
      "tr_title": "Lying Leg Curl (Makine)",
      "media_type": "video",
      "superset_id": null,
      "zh_cn_title": "躺着腿弯举（机）",
      "zh_tw_title": "躺著腿彎舉（機）",
      "muscle_group": "hamstrings",
      "rest_seconds": 120,
      "exercise_type": "weight_reps",
      "other_muscles": [],
      "thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/05861201-Lever-Lying-Leg-Curl_Thighs_thumbnail@3x.jpg",
      "equipment_category": "machine",
      "exercise_template_id": "B8127AD1",
      "volume_doubling_enabled": false,
      "custom_exercise_image_url": null,
      "custom_exercise_image_thumbnail_url": "https://pump-app.s3.eu-west-2.amazonaws.com/exercise-thumbnails/05861201-Lever-Lying-Leg-Curl_Thighs_thumbnail@3x.jpg"
    }
  ],
  "created_at": "2025-01-21T17:43:48.804Z",
  "image_urls": [],
  "is_private": false,
  "like_count": 1,
  "routine_id": "0bb90234-0ee2-4a31-bcea-1133a404ee16",
  "start_time": 1737478514,
  "updated_at": "2025-01-21T19:52:45.499Z",
  "apple_watch": true,
  "description": "",
  "like_images": [
    "https://d2l9nsnmtah87f.cloudfront.net/profile-images/gigi724-451c5d23-7e7c-4564-8113-7fbf719716f1.jpg"
  ],
  "nth_workout": 467,
  "wearos_watch": false,
  "comment_count": 0,
  "profile_image": "https://d2l9nsnmtah87f.cloudfront.net/profile-images/vertislav-2bc7c904-634c-4063-ac6c-458022a4a36e.jpg",
  "is_liked_by_user": false,
  "estimated_volume_kg": 13695
}
"""


def normalize_workout_to_sets(workout):
    # Workout-level fields to discard
    discard_workout = {
        "media",
        "comments",
        "short_id",
        "verified",
        "image_urls",
        "description",
        "like_images",
        "profile_image",
        "is_liked_by_user",
        "apple_watch",
        "wearos_watch",
        "is_private",
        "like_count",
    }
    # Exercise-level fields to discard
    discard_exercise = {
        "url",
        "notes",
        "de_title",
        "es_title",
        "fr_title",
        "it_title",
        "ja_title",
        "ko_title",
        "pt_title",
        "ru_title",
        "tr_title",
        "media_type",
        "superset_id",
        "zh_cn_title",
        "zh_tw_title",
        "thumbnail_url",
        "custom_exercise_image_url",
        "custom_exercise_image_thumbnail_url",
        "volume_doubling_enabled",
    }
    rows = []
    workout_fields = {
        k: v
        for k, v in workout.items()
        if k != "exercises" and k not in discard_workout
    }
    for exercise in workout.get("exercises", []):
        exercise_fields = {}
        for k, v in exercise.items():
            if k == "sets":
                continue
            if k.endswith("title") and k != "title":
                continue  # keep only 'title' (English)
            if k in discard_exercise:
                continue
            exercise_fields[f"exercise_{k}"] = v
        for s in exercise.get("sets", []):
            set_row = workout_fields.copy()
            set_row.update(exercise_fields)
            for set_k, set_v in s.items():
                set_row[f"set_{set_k}"] = set_v
            rows.append(set_row)
    return rows


# Usage
workout_dict = json.loads(workout_json)
rows = normalize_workout_to_sets(workout_dict)

# Write to CSV
if rows:
    with open("workouts_normalized.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("CSV file 'workouts_normalized.csv' written.")
else:
    print("No exercises found.")
