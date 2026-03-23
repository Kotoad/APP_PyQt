<?php
// ─────────────────────────────────────────────
//  OmniBoard Studio – App-start tracking endpoint
//  Called by the desktop app on launch.
//  GET / POST params: version, platform, id
// ─────────────────────────────────────────────

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once __DIR__ . '/../Admin/config.php';

// ── Collect & sanitise parameters ──────────────────────────────────────────
$version      = substr(preg_replace('/[^a-zA-Z0-9._\-]/', '', $_REQUEST['version']  ?? ''), 0, 32);
$platform     = in_array($_REQUEST['platform'] ?? '', ['windows', 'linux', 'macos'], true)
                    ? $_REQUEST['platform']
                    : 'unknown';
$anonymous_id = substr(preg_replace('/[^a-zA-Z0-9\-]/', '', $_REQUEST['id'] ?? ''), 0, 64);

// ── Anonymise IP ────────────────────────────────────────────────────────────
$raw_ip  = $_SERVER['HTTP_CF_CONNECTING_IP']
        ?? $_SERVER['HTTP_X_FORWARDED_FOR']
        ?? $_SERVER['REMOTE_ADDR']
        ?? '';
// Take only the first IP if there is a comma-separated list
$raw_ip  = trim(explode(',', $raw_ip)[0]);
$ip_hash = substr(hash('sha256', $raw_ip . IP_HASH_SALT), 0, 12);

// ── Build the new log entry ─────────────────────────────────────────────────
$entry = [
    'timestamp'    => date('c'),
    'version'      => $version,
    'platform'     => $platform,
    'ip_hash'      => $ip_hash,
    'anonymous_id' => $anonymous_id,
];

// ── Read / write app_starts.json ────────────────────────────────────────────
$file = DATA_DIR . 'app_starts.json';

$entries = [];
if (file_exists($file)) {
    $raw = file_get_contents($file);
    if ($raw !== false) {
        $decoded = json_decode($raw, true);
        if (is_array($decoded)) {
            $entries = $decoded;
        }
    }
}

$entries[] = $entry;

// Keep the newest 10 000 entries only
if (count($entries) > 10000) {
    $entries = array_slice($entries, -10000);
}

// Ensure the data directory exists and write atomically
if (!is_dir(DATA_DIR)) {
    mkdir(DATA_DIR, 0755, true);
}

$tmp = $file . '.tmp';
if (file_put_contents($tmp, json_encode($entries, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX) !== false) {
    rename($tmp, $file);
}

echo json_encode(['status' => 'ok']);
