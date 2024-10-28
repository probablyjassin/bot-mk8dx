FROM selenium/standalone-chrome:latest

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Add volume for data
VOLUME /app/data

# Define environment variables
ENV DISCORD_TOKEN = ""
ENV MONGO_URI = ""
ENV LOUNGE_DB = ""
ENV GUILD_IDS = ''
ENV LOG_CHANNEL_ID = ''
ENV REGISTER_CHANNEL_ID = ''

CMD ["python", "-u", "main.py"]
