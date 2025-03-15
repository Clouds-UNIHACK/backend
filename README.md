## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
    - [Back-end Setup](#back-end-setup)
- [Running Instructions](#running-instructions)

## Prerequisites

Before you begin, ensure you have met the following requirements:
- **Python** (version 3.8 or above) 
- **Pip** for installing Python packages

Please check the version of these requirements:
```bash
python --version // For Python
pip --version // For Pip
```
## Setup Instructions

### Back-end Setup
1. Navigate to the back-end directory:
```bash
cd backend
```

2. You can install the required libraries using pip:
```bash
pip install -r requirements.txt
```

3. Initialize database:
```bash
python utils/init_db.py
```
## Running Instructions
4. Navigate to the back-end directory:
```bash
cd backend
```

5. Open FastAPI server
```bash
uvicorn main:app --reload
```