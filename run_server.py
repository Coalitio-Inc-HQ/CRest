import uvicorn
from src.app import app
from src.settings import settings

# import src.check_server # не убирать


uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)

# можно ли открыто хранить токены в бд?
# индентифицировать ли отдельного пользователя?