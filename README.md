# ServiceNow Incident Azure Function (Python)

This Azure Function loads ServiceNow credentials from a `.env` file and returns all incidents from the ServiceNow `incident` table.

## Setup
1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
2. Create a `.env` file at the repository root.

## .env example
```ini
SERVICENOW_URL=https://YOUR_INSTANCE.service-now.com
SERVICENOW_USER=your-username
SERVICENOW_PASS=your-password
```

## Run locally
```powershell
func start
```

## Call the function
```powershell
curl "http://localhost:7071/api/GetIncidents"
```

## Notes
- The function also accepts query parameters `url`, `username`, and `password`, but environment values from `.env` are preferred.
- `local.settings.json` is used only for Azure Functions runtime settings, not for ServiceNow credentials.
