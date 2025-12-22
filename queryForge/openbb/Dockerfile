FROM python:3.11-slim

WORKDIR /openbb

# Install OpenBB and any other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: copy your script if you're using main.py
COPY . .

# To run a specific script, you can replace the above CMD with:
CMD ["python", "main.py"]