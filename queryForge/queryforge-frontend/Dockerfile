
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY . .

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
