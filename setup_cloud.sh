#!/bin/bash

# PGRKAM Digital Assistant - Google Cloud Setup Script
# This script sets up the required Google Cloud resources

set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
BUCKET_NAME="pgrkam-chatbot-storage"
FIRESTORE_DATABASE="pgrkam-chatbot-db"

echo "☁️  Setting up Google Cloud resources for PGRKAM Digital Assistant"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Please log in to Google Cloud:"
    gcloud auth login
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Create Cloud Storage bucket
echo "🪣 Creating Cloud Storage bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME || echo "Bucket already exists"

# Create Firestore database
echo "🔥 Creating Firestore database..."
gcloud firestore databases create --location=$REGION --project=$PROJECT_ID || echo "Database already exists"

# Create service account for the application
echo "👤 Creating service account..."
gcloud iam service-accounts create pgrkam-chatbot-sa \
    --display-name="PGRKAM Chatbot Service Account" \
    --description="Service account for PGRKAM Digital Assistant" || echo "Service account already exists"

# Grant necessary permissions
echo "🔑 Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:pgrkam-chatbot-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:pgrkam-chatbot-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:pgrkam-chatbot-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create secrets for API keys
echo "🔐 Creating secrets..."
echo "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- --project=$PROJECT_ID || echo "Secret already exists"

# Create environment file template
cat > .env.cloud << EOF
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=$REGION
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# API Keys (will be set from secrets in production)
GEMINI_API_KEY=\$(gcloud secrets versions access latest --secret=gemini-api-key --project=$PROJECT_ID)

# Application Settings
APP_NAME=PGRKAM Digital Assistant
APP_VERSION=1.0.0
DEBUG=False

# Language Settings
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,hi,pa

# Audio Settings
SPEECH_RATE=150
SPEECH_VOLUME=0.8
VOICE_GENDER=male

# RAG Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3

# Gemini Model Settings
GEMINI_MODEL=gemini-pro
MAX_TOKENS=2048
TEMPERATURE=0.7

# Google Cloud Settings
USE_VERTEX_AI=true
CLOUD_STORAGE_BUCKET=$BUCKET_NAME

# Job Recommendation Settings
MAX_JOB_RECOMMENDATIONS=5
PREFERENCE_WEIGHT=0.7
EOF

echo ""
echo "✅ Google Cloud setup completed successfully!"
echo ""
echo "📋 Resources created:"
echo "- Project: $PROJECT_ID"
echo "- APIs enabled: Cloud Build, Cloud Run, Container Registry, AI Platform, Firestore, Storage"
echo "- Storage bucket: gs://$BUCKET_NAME"
echo "- Firestore database: $FIRESTORE_DATABASE"
echo "- Service account: pgrkam-chatbot-sa@$PROJECT_ID.iam.gserviceaccount.com"
echo "- Secret: gemini-api-key"
echo ""
echo "🔧 Next steps:"
echo "1. Set your Gemini API key: gcloud secrets versions add gemini-api-key --data-file=-"
echo "2. Deploy the application: ./deploy.sh"
echo "3. Configure custom domain (optional)"
echo ""
echo "📊 To view resources:"
echo "- Storage: https://console.cloud.google.com/storage/browser"
echo "- Firestore: https://console.cloud.google.com/firestore"
echo "- AI Platform: https://console.cloud.google.com/ai-platform"
echo "- Cloud Run: https://console.cloud.google.com/run"
