# LAME_FAIR_by_Design

LAME_FAIR_by_Design is a Django-based application that allows you to upload metadata and images, generate NeXus files, and view stored files locally. This project demonstrates how to organize and manage experimental data using Django’s built-in structures and a local file storage backend.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Optional production deployment](#optional-production-deployment)
5. [Project Structure](#project-structure)

---

## Prerequisites
1. **Python 3.8+**: Ensure you have a recent Python version installed.
2. **Git**: for cloning or downloading the project.
3. **Virtual environment (recommended)**: use `venv`, `virtualenv`, or Conda to avoid Python package conflicts.

---

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/NicolaPerin/Thesis_Code.git

2. **Navigate to the project folder**:
   ```bash
   cd Thesis_Code/area-rit

3. **Create a virtual environment, activate it and install the required packages**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

4. **Configure Django**:
   - Create a .env file in the project root directory using this command:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(f'DJANGO_SECRET_KEY=\"{get_random_secret_key()}\"\\nDJANGO_DEBUG=True')" > .env

---

## Usage

1. **Start the Django development server**:
   ```bash
   python manage.py runserver 8000

2. **Access the application**:
   - Open your web browser and go to http://127.0.0.1:8000/.

3. **Create a new experiment**:
   - Navigate to “Create New Experiment” and fill out the required details.
   - You can find a pair of images in the example_images folder
   - The NeXus file will be created in /tmp then moved to your local storage folder (local_storage).

4. **View stored files**:
   - Click on “View Uploaded Files” to see the list of NeXus files. You can then download or view embedded images directly.

---

## Optional production deployment

The `feature/virtualorfeo_integration` branch contains Kubernetes manifests and Helm charts to run this application in a production cluster.  
**Note:** Reproducing that setup requires a Kubernetes environment and associated infrastructure, which may not be available to evaluators.  
For a fully reproducible, local development environment, please continue to use the `main` branch (as documented above).

---

## Project structure
```
   lame_fair_by_design/
   ├─ file_manager/
   │  ├─ views.py           # Core logic for uploading, creating, and viewing files
   │  ├─ templates/         # Django templates for UI
   │  ├─ static/            # Static files (CSS, JS, images)
   │  └─ ...               
   ├─ local_storage/        # Stores created NeXus files locally
   ├─ minio_app/            # Django settings and URL routing   
   │  ├─ settings.py        # Main Django settings file (where you load SECRET_KEY and DEBUG mode)
   │  └─ ...
   ├─ requirements.txt      # Project dependencies
   ├─ manage.py             # Django management commands   
   └─ ...
