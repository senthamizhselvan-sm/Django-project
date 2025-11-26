# 🔧 Fix Render Environment Variables

## 🚨 Current Issue
The MongoDB URI contains unescaped `@` symbol causing `InvalidURI` error in production.

## ✅ Solution Steps

### 1. **Access Render Dashboard**
- Go to [render.com](https://render.com)
- Click on your service: `django-project-2-9xay`
- Navigate to **Environment** tab

### 2. **Update Environment Variables**
Replace the current values with these corrected ones:

```env
MONGO_URI=mongodb+srv://senthamizhselvansm_db_user:Selva%40123@cluster0.uufkp3i.mongodb.net/?appName=Cluster0
DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-production-key-here
MONGO_DB_NAME=radiology_db
```

### 3. **What Changed**
- ❌ **Old**: `Selva@123` (causes InvalidURI error)
- ✅ **New**: `Selva%40123` (URL-encoded `@` symbol)
- ✅ **Security**: `DEBUG=False` for production

### 4. **After Updating**
- Click **Save Changes**
- Render will automatically redeploy with new environment variables
- Monitor the deployment logs for success

### 5. **Expected Result**
- ✅ No more `InvalidURI` errors
- ✅ User registration will work
- ✅ MongoDB connections established
- ✅ Production security enabled

## 🔍 **Verification**
After redeployment, test:
1. Visit: `https://django-project-2-9xay.onrender.com/register/`
2. Try registering a new user
3. Should work without MongoDB URI errors

## 🚨 **Critical Note**
Environment variables in Render dashboard override any `.env` file settings. Local `.env` is already fixed, but production needs manual update in Render dashboard.