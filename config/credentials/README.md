# Credentials Folder (config/credentials)

This folder stores sensitive credential files for API authentication.

## Security Notes

⚠️ **CRITICAL**: This folder is gitignored. Never commit credential files to version control.

## Files to Store Here

### Broker Certificates
- `*.pfx` - Shioaji (永豐金證券) certificate files
- Certificate files should be referenced in `.env` file

### Google Drive Token
- `google_token.json` - Google OAuth token for Drive API access

### Example Structure
```
config/credentials/
├── .gitkeep
├── README.md
├── google_token.json          # Google Drive token
├── junting_Sinopac.pfx        # User's broker certificate
└── alan_Sinopac.pfx           # Another user's certificate
```

## Usage in .env

Reference these files in your `.env` file:

```bash
# Google Drive Token
GOOGLE_TOKEN_PATH=./config/credentials/google_token.json

# Shioaji Certificate
SHIOAJI_CERT_PATH=./config/credentials/junting_Sinopac.pfx
```

## Docker Path Mapping

When running in Docker, paths are mounted as:
- Host: `./config/credentials/your_cert.pfx`
- Container: `/app/config/credentials/your_cert.pfx`

Make sure your `.env` uses the correct path format for your environment.
