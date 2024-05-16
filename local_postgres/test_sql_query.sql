SELECT * FROM sets 
	WHERE exercise_id IN
		(SELECT exercise_id FROM exercises
			WHERE workout_id = 'E952F27A-F613-40C8-A776-4858C1656DD9');