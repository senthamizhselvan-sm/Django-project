# MongoDB Setup Guide for Radiology AI System

## Installing MongoDB on Windows

### Option 1: MongoDB Community Server (Recommended)

1. **Download MongoDB**
   - Visit: https://www.mongodb.com/try/download/community
   - Select: Windows x64
   - Download the MSI installer

2. **Install MongoDB**
   - Run the downloaded `.msi` file
   - Choose "Complete" installation
   - Select "Run service as Network Service user"
   - Install MongoDB as a Windows Service
   - Install MongoDB Compass (GUI tool) - Optional

3. **Verify Installation**
   ```powershell
   mongod --version
   ```

4. **Start MongoDB Service**
   - MongoDB should start automatically as a Windows service
   - Or manually start:
   ```powershell
   net start MongoDB
   ```

5. **Connect to MongoDB**
   ```powershell
   mongosh
   ```

### Option 2: Using Docker (Alternative)

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Verifying MongoDB Connection

1. **Using MongoDB Compass**
   - Open MongoDB Compass
   - Connect to: `mongodb://localhost:27017`
   - Look for `radiology_db` database (will be created automatically)

2. **Using MongoDB Shell**
   ```javascript
   mongosh
   use radiology_db
   db.users.find()
   ```

## MongoDB Configuration for Project

The application is configured to connect to:
- **URI**: `mongodb://localhost:27017/`
- **Database**: `radiology_db`
- **Collection**: `users`

### Configuration Location
File: `radiology/settings.py`
```python
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DB_NAME = 'radiology_db'
```

## Troubleshooting

### MongoDB Not Starting
```powershell
# Check if MongoDB service is running
Get-Service -Name MongoDB

# Start MongoDB service
Start-Service -Name MongoDB
```

### Connection Refused Error
1. Check if MongoDB is running
2. Verify the port 27017 is not blocked
3. Check firewall settings

### Port Already in Use
```powershell
# Find process using port 27017
netstat -ano | findstr :27017

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

## Sample MongoDB Commands

### View All Databases
```javascript
show dbs
```

### Switch to Radiology Database
```javascript
use radiology_db
```

### View All Users
```javascript
db.users.find().pretty()
```

### Count Users
```javascript
db.users.countDocuments()
```

### Find User by Email
```javascript
db.users.findOne({email: "test@example.com"})
```

### Delete a User
```javascript
db.users.deleteOne({email: "test@example.com"})
```

### Drop Users Collection
```javascript
db.users.drop()
```

## Security Recommendations (For Production)

1. **Enable Authentication**
   ```javascript
   use admin
   db.createUser({
     user: "radiologyAdmin",
     pwd: "securePassword",
     roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase"]
   })
   ```

2. **Update Connection URI**
   ```python
   MONGO_URI = 'mongodb://radiologyAdmin:securePassword@localhost:27017/'
   ```

3. **Enable SSL/TLS**
4. **Set up IP Whitelisting**
5. **Regular Backups**

## Backup Commands

### Backup Database
```bash
mongodump --db radiology_db --out C:\mongodb_backup
```

### Restore Database
```bash
mongorestore --db radiology_db C:\mongodb_backup\radiology_db
```

---

**Note**: For development, the default configuration without authentication is acceptable. For production deployment, implement proper security measures.
