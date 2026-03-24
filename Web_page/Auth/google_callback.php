<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – Google OAuth callback
// ─────────────────────────────────────────────

    

ini_set('display_errors', 1);
error_reporting(E_ALL);

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

// ── Validate state ───────────────────────────────────────────────────────────
if (empty($_GET['state']) || $_GET['state'] !== ($_SESSION['oauth_state'] ?? '')) {
    $received = $_GET['state'] ?? 'None';
    $expected = $_SESSION['oauth_state'] ?? 'None';
    die("OAuth state mismatch. Received state: " . htmlspecialchars($received) . " | Expected: " . htmlspecialchars($expected));
}
unset($_SESSION['oauth_state']);

if (empty($_GET['code'])) {
    die('Google OAuth did not return an authorisation code.');
}

$protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
$redirect_uri = $protocol . '://' . $_SERVER['HTTP_HOST'] . '/Auth/google_callback.php';

// ── Exchange code for access token ───────────────────────────────────────────
$token_data = _google_post('https://oauth2.googleapis.com/token', [
    'code'          => $_GET['code'],
    'client_id'     => GOOGLE_CLIENT_ID,
    'client_secret' => GOOGLE_CLIENT_SECRET,
    'redirect_uri'  => $redirect_uri,
    'grant_type'    => 'authorization_code',
]);

if (empty($token_data['access_token'])) {
    echo "<h3>Failed to obtain Google access token. Raw response:</h3><pre>";
    print_r($token_data);
    die("</pre>");
}

$access_token = $token_data['access_token'];

// ── Fetch user info ──────────────────────────────────────────────────────────
$user_info = _google_get('https://www.googleapis.com/oauth2/v2/userinfo', $access_token);

if (empty($user_info['email']) || empty($user_info['verified_email'])) {
    echo "<h3>No verified email address found. Raw user info:</h3><pre>";
    print_r($user_info);
    die("</pre>");
}

$primary_email = strtolower($user_info['email']);

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
function _google_post(string $url, array $fields): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query($fields),
        CURLOPT_HTTPHEADER     => ['Content-Type: application/x-www-form-urlencoded'],
        CURLOPT_TIMEOUT        => 10,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response ?: '{}', true) ?? [];
}

function _google_get(string $url, string $token): array
{
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ['Authorization: Bearer ' . $token],
        CURLOPT_TIMEOUT        => 10,
    ]);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response ?: '{}', true) ?? [];
}