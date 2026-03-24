<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – GitHub OAuth callback
// ─────────────────────────────────────────────

$session_lifetime = 60 * 60 * 24 * 30; // 30 days

// 1. Tell the server not to delete the session file for 30 days
ini_set('session.gc_maxlifetime', $session_lifetime);

// 2. Determine cookie domain dynamically to support localhost testing and production
$current_host = $_SERVER['HTTP_HOST'];
$cookie_domain = ($current_host === 'localhost') ? 'localhost' : '.omniboardstudio.cz';

// 3. Set cookie parameters including wildcard domain (note the leading dot)
session_set_cookie_params([
    'lifetime' => $session_lifetime,
    'path'     => '/',
    'domain'   => $cookie_domain,
    'secure'   => ($current_host !== 'localhost'), // Requires HTTPS in production
    'httponly' => true,
    'samesite' => 'Lax'
]);

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

require_once __DIR__ . '/../Admin/config.php';

// ── Validate state to prevent CSRF ──────────────────────────────────────────
if (empty($_GET['state']) || $_GET['state'] !== ($_SESSION['oauth_state'] ?? '')) {
    $_SESSION['oauth_error'] = 'OAuth state mismatch. Please try again.';
    header('Location: /');
    exit;
}
unset($_SESSION['oauth_state']);

if (empty($_GET['code'])) {
    $_SESSION['oauth_error'] = 'GitHub OAuth did not return an authorisation code.';
    header('Location: /');
    exit;
}

// ── Exchange code for access token ──────────────────────────────────────────
$token_response = _github_post('https://github.com/login/oauth/access_token', [
    'client_id'     => GITHUB_CLIENT_ID,
    'client_secret' => GITHUB_CLIENT_SECRET,
    'code'          => $_GET['code'],
]);

if (empty($token_response['access_token'])) {
    $_SESSION['oauth_error'] = 'Failed to obtain GitHub access token.';
    header('Location: /');
    exit;
}

$access_token = $token_response['access_token'];

// ── Fetch authenticated user info ────────────────────────────────────────────
$user = _github_get('https://api.github.com/user', $access_token);
if (empty($user['login'])) {
    $_SESSION['oauth_error'] = 'Failed to fetch GitHub user info.';
    header('Location: /');
    exit;
}

// ── Fetch verified primary email ─────────────────────────────────────────────
$emails       = _github_get('https://api.github.com/user/emails', $access_token);
$primary_email = '';

if (is_array($emails)) {
    foreach ($emails as $email_entry) {
        if (!empty($email_entry['primary']) && !empty($email_entry['verified'])) {
            $primary_email = strtolower($email_entry['email']);
            break;
        }
    }
    // Fall back to any verified email
    if ($primary_email === '') {
        foreach ($emails as $email_entry) {
            if (!empty($email_entry['verified'])) {
                $primary_email = strtolower($email_entry['email']);
                break;
            }
        }
    }
}

if ($primary_email === '') {
    $_SESSION['oauth_error'] = 'No verified email address found on your GitHub account.';
    header('Location: /');
    exit;
}

// ── Load / update SQL Database ───────────────────────────────────────────────
$now = date('Y-m-d H:i:s'); // Changed to standard SQL DATETIME format

// Identify the account: Use active session if linking, otherwise use GitHub email
$account_key = $_SESSION['user_email'] ?? $primary_email;

// Fetch existing user from database
$stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
$stmt->execute([$account_key]);
$existing_user = $stmt->fetch();

if (!$existing_user) {
    // Brand new user registration
    $providers = [
        'github' => [
            'email'           => $primary_email,
            'github_username' => $user['login'] ?? '',
            'avatar_url'      => $user['avatar_url'] ?? '',
            'linked_at'       => $now
        ]
    ];

    $stmt = $pdo->prepare("INSERT INTO users (email, registered_at, last_login, source, github_username, avatar_url, providers) VALUES (?, ?, ?, ?, ?, ?, ?)");
    $stmt->execute([
        $account_key,
        $now,
        $now,
        'multiple',
        $user['login'] ?? '',
        $user['avatar_url'] ?? '',
        json_encode($providers)
    ]);
} else {
    // Existing user login / account linking
    $providers = json_decode($existing_user['providers'], true) ?? [];
    
    $providers['github'] = [
        'email'           => $primary_email,
        'github_username' => $user['login'] ?? '',
        'avatar_url'      => $user['avatar_url'] ?? '',
        'linked_at'       => $providers['github']['linked_at'] ?? $now
    ];

    $stmt = $pdo->prepare("UPDATE users SET last_login = ?, github_username = ?, avatar_url = ?, providers = ? WHERE email = ?");
    $stmt->execute([
        $now,
        $user['login'] ?? '',
        $user['avatar_url'] ?? '',
        json_encode($providers),
        $account_key
    ]);
}

// Set session and redirect to the new Settings page
$_SESSION['user_email'] = $account_key;
header('Location: /Auth/settings.php');
exit;

// ── Helpers ──────────────────────────────────────────────────────────────────
function _github_post(string $url, array $fields): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query($fields),
        CURLOPT_HTTPHEADER     => [
            'Accept: application/json',
            'User-Agent: OmniBoard-Studio/1.0',
        ],
        CURLOPT_TIMEOUT        => 10,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response ?: '{}', true) ?? [];
}

function _github_get(string $url, string $token): mixed
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . $token,
            'Accept: application/vnd.github+json',
            'User-Agent: OmniBoard-Studio/1.0',
        ],
        CURLOPT_TIMEOUT        => 10,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response ?: '[]', true);
}
