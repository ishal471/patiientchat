Steps:
1. Export openai api key, langsmith variables for token manament, aws secret manager variablees to environment variables (aws has gemini etc keys)
2. In settings.py change postgress db details
3. change path to manage.py dircetory and the run command python manage.py runserver
4. open the prompted url append /chat/ for AI Health bot

Note:
1. This project has langsmith tracking
2. Can switch between models ex openai and google gemini
3. Can handle long conversations with inclustion of conersation summary buffer
4. Secret keys are managed with aws secret key manager , (this is industry pracitice)
