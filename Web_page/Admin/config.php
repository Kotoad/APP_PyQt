<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – Admin Configuration
// ─────────────────────────────────────────────

// PostHog REST API credentials (server-side only)
// Get your personal API key from: https://eu.posthog.com/settings/user-api-keys
define('POSTHOG_PERSONAL_API_KEY', 'phx_REPLACE_WITH_YOUR_PERSONAL_API_KEY');
define('POSTHOG_PROJECT_ID',       'REPLACE_WITH_YOUR_PROJECT_ID');   // numeric, e.g. 12345

// PostHog project settings (used for JS snippet & API base)
define('POSTHOG_API_HOST',    'https://eu.posthog.com');
define('POSTHOG_PROJECT_KEY', 'phc_Mluykd4ZFp3kGqZaKOW5ZVppq7uvZhNzrGf2h9ZaRrQ');

// GitHub API token (optional – raises rate limit from 60 to 5000 req/h)
// Create at: https://github.com/settings/tokens  (public_repo scope is enough)
define('GITHUB_TOKEN', 'REPLACE_WITH_YOUR_GITHUB_PERSONAL_TOKEN');
define('GITHUB_REPO',  'Kotoad/APP_PyQt');

// GitHub OAuth application credentials
// Register at: https://github.com/settings/applications/new
// Callback URL: https://omniboardstudio.cz/Auth/github_callback.php
define('GITHUB_CLIENT_ID',     'REPLACE_WITH_GITHUB_OAUTH_CLIENT_ID');
define('GITHUB_CLIENT_SECRET', 'REPLACE_WITH_GITHUB_OAUTH_CLIENT_SECRET');

// Google OAuth application credentials
// Create at: https://console.cloud.google.com/apis/credentials
// Callback URL: https://omniboardstudio.cz/Auth/google_callback.php
define('GOOGLE_CLIENT_ID',     'REPLACE_WITH_GOOGLE_OAUTH_CLIENT_ID');
define('GOOGLE_CLIENT_SECRET', 'REPLACE_WITH_GOOGLE_OAUTH_CLIENT_SECRET');

// Admin login credentials
// Username stored in plain text; password stored as bcrypt hash.
// Default password: changeme123  – change this before deploying!
// To regenerate: php -r "echo password_hash('your_password', PASSWORD_BCRYPT);"
define('ADMIN_USERNAME',      'admin');
define('ADMIN_PASSWORD_HASH', '$2y$12$YqFV5kpNZ.K8PSIBnIHXcuI8RyMfgV5S3LFy1Bk5gzW0PQHG9Y4cW');

// Data directory (writable by the web server)
define('DATA_DIR', __DIR__ . '/../data/');

// Secret salt used for IP anonymisation in app_starts.json
// Set this to a long random string. Must never change once data has been collected.
define('IP_HASH_SALT', 'REPLACE_WITH_A_LONG_RANDOM_SECRET_STRING_32_CHARS_MIN');

// Session lifetime in seconds (4 hours)
define('ADMIN_SESSION_LIFETIME', 4 * 60 * 60);
