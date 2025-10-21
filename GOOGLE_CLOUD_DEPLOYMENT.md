# 🚀 Google Cloud Deployment Guide - PGRKAM Digital Assistant

This guide will help you deploy the PGRKAM Digital Assistant to Google Cloud using Gemini API and Google Cloud services.

## 📋 Prerequisites

1. **Google Cloud Account**: Create a Google Cloud account at https://cloud.google.com
2. **Google Cloud CLI**: Install gcloud CLI from https://cloud.google.com/sdk/docs/install
3. **Gemini API Key**: Get your API key from https://makersuite.google.com/app/apikey
4. **Docker**: Install Docker for containerization

## 🏗️ Architecture Overview

The deployment uses the following Google Cloud services:
- **Cloud Run**: Serverless container platform for the web application
- **Gemini API**: Google's generative AI for natural language processing
- **Firestore**: NoSQL database for user data and conversations
- **Cloud Storage**: File storage for documents and assets
- **Vertex AI**: Optional advanced AI services for embeddings and vector search
- **Cloud Build**: CI/CD pipeline for automated deployments

## 🔧 Setup Instructions

### Step 1: Initial Google Cloud Setup

1. **Create a new project** or select an existing one:
   ```bash
   gcloud projects create your-project-id
   gcloud config set project your-project-id
   ```

2. **Run the cloud setup script**:
   ```bash
   chmod +x setup_cloud.sh
   ./setup_cloud.sh
   ```

3. **Set your Gemini API key**:
   ```bash
   echo "your-gemini-api-key" | gcloud secrets versions add gemini-api-key --data-file=- --project=your-project-id
   ```

### Step 2: Environment Configuration

Create a `.env` file with your configuration:
```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
APP_NAME=PGRKAM Digital Assistant
APP_VERSION=1.0.0
DEBUG=False

# Language Settings
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,hi,pa

# Gemini Model Settings
GEMINI_MODEL=gemini-pro
MAX_TOKENS=2048
TEMPERATURE=0.7

# Google Cloud Settings
USE_VERTEX_AI=true
CLOUD_STORAGE_BUCKET=your-bucket-name
```

### Step 3: Deploy to Google Cloud

1. **Run the deployment script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Alternative: Manual deployment**:
   ```bash
   # Build and push image
   gcloud builds submit --tag gcr.io/your-project-id/pgrkam-chatbot .
   
   # Deploy to Cloud Run
   gcloud run deploy pgrkam-chatbot \
       --image gcr.io/your-project-id/pgrkam-chatbot \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated \
       --port 8080 \
       --memory 2Gi \
       --cpu 1 \
       --max-instances 10
   ```

## 🌐 Accessing Your Application

After deployment, you'll receive a URL like:
```
https://pgrkam-chatbot-xxxxx-uc.a.run.app
```

### Health Check
Test if your application is running:
```bash
curl https://your-service-url/health
```

### Web Interface
Visit the URL in your browser to access the chatbot interface.

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | Required |
| `GOOGLE_CLOUD_LOCATION` | Deployment region | `us-central1` |
| `GEMINI_MODEL` | Gemini model to use | `gemini-pro` |
| `USE_VERTEX_AI` | Enable Vertex AI features | `true` |
| `MAX_TOKENS` | Maximum response tokens | `2048` |
| `TEMPERATURE` | Response creativity | `0.7` |

### Scaling Configuration

The application is configured with:
- **Memory**: 2GB
- **CPU**: 1 vCPU
- **Max Instances**: 10
- **Min Instances**: 1
- **Timeout**: 300 seconds

## 📊 Monitoring and Logs

### View Logs
```bash
gcloud logs tail --service=pgrkam-chatbot --region=us-central1
```

### Monitor Performance
Visit the Google Cloud Console:
- **Cloud Run**: https://console.cloud.google.com/run
- **Logs**: https://console.cloud.google.com/logs
- **Monitoring**: https://console.cloud.google.com/monitoring

## 🔒 Security Considerations

1. **API Keys**: Stored in Google Secret Manager
2. **Authentication**: Service account with minimal permissions
3. **HTTPS**: Automatic SSL/TLS encryption
4. **CORS**: Configured for web access
5. **Input Validation**: All user inputs are validated

## 🚀 Advanced Features

### Custom Domain
To use a custom domain:

1. **Map your domain** in Cloud Run console
2. **Update DNS records** to point to Cloud Run
3. **Configure SSL certificate** (automatic with Google-managed certificates)

### Database Options

#### Option 1: Firestore (Default)
- NoSQL document database
- Automatic scaling
- Real-time updates
- Good for user preferences and chat history

#### Option 2: Cloud SQL
For PostgreSQL database:

1. **Create Cloud SQL instance**:
   ```bash
   gcloud sql instances create pgrkam-db \
       --database-version=POSTGRES_13 \
       --tier=db-f1-micro \
       --region=us-central1
   ```

2. **Create database**:
   ```bash
   gcloud sql databases create chatbot --instance=pgrkam-db
   ```

3. **Update environment variables**:
   ```env
   CLOUD_SQL_CONNECTION_NAME=your-project:us-central1:pgrkam-db
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_NAME=chatbot
   ```

### Vector Search with Vertex AI

Enable advanced vector search:

1. **Enable Vertex AI API**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

2. **Set environment variable**:
   ```env
   USE_VERTEX_AI=true
   ```

## 🔄 CI/CD Pipeline

The included `cloudbuild.yaml` enables automated deployments:

1. **Connect to GitHub** (optional):
   ```bash
   gcloud builds triggers create github \
       --repo-name=your-repo \
       --repo-owner=your-username \
       --branch-pattern="^main$" \
       --build-config=cloudbuild.yaml
   ```

2. **Manual deployment**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Deployment Fails
```bash
# Check build logs
gcloud builds log --stream

# Verify permissions
gcloud projects get-iam-policy your-project-id
```

#### 2. API Errors
```bash
# Verify API key
gcloud secrets versions access latest --secret=gemini-api-key

# Check API quotas
gcloud logging read "resource.type=api"
```

#### 3. Database Connection Issues
```bash
# Test Firestore connection
gcloud firestore databases list

# Check service account permissions
gcloud projects get-iam-policy your-project-id \
    --flatten="bindings[].members" \
    --filter="bindings.members:pgrkam-chatbot-sa@your-project-id.iam.gserviceaccount.com"
```

### Performance Optimization

1. **Enable CDN**: Use Cloud CDN for static assets
2. **Database Indexing**: Create indexes for frequently queried fields
3. **Caching**: Implement response caching for common queries
4. **Connection Pooling**: Use connection pooling for database connections

## 📈 Scaling

### Horizontal Scaling
- **Auto-scaling**: Configured to scale based on CPU and requests
- **Load Balancing**: Automatic with Cloud Run
- **Regional Deployment**: Deploy to multiple regions for global access

### Vertical Scaling
- **Memory**: Increase to 4GB or 8GB for heavy workloads
- **CPU**: Increase to 2 or 4 vCPUs for faster processing

## 💰 Cost Optimization

### Free Tier Limits
- **Cloud Run**: 2 million requests/month
- **Firestore**: 50,000 reads/day, 20,000 writes/day
- **Cloud Storage**: 5GB storage
- **Cloud Build**: 120 build-minutes/day

### Cost Monitoring
```bash
# Set up billing alerts
gcloud billing budgets create \
    --billing-account=your-billing-account \
    --display-name="PGRKAM Chatbot Budget" \
    --budget-amount=100USD
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Rebuild and deploy
./deploy.sh

# Or use Cloud Build trigger
git push origin main
```

### Update Dependencies
```bash
# Update requirements.txt
pip freeze > requirement.txt

# Rebuild image
gcloud builds submit --tag gcr.io/your-project-id/pgrkam-chatbot .
```

### Backup Data
```bash
# Export Firestore data
gcloud firestore export gs://your-backup-bucket/backup-$(date +%Y%m%d)
```

## 📞 Support

### Google Cloud Support
- **Documentation**: https://cloud.google.com/docs
- **Community**: https://cloud.google.com/community
- **Support Plans**: https://cloud.google.com/support

### Application Support
- **Logs**: Check Cloud Run logs for errors
- **Monitoring**: Use Cloud Monitoring for performance metrics
- **Debugging**: Enable debug mode for detailed logging

---

**🎉 Your PGRKAM Digital Assistant is now deployed on Google Cloud!**

For additional help, refer to:
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)
