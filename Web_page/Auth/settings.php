<?php
require_once __DIR__ . '/../i18n.php'; // Important to load language

require_once __DIR__ . '/../Admin/config.php';

// Redirect to home if not logged in
if (empty($_SESSION['user_email'])) {
    header('Location: /');
    exit;
}

$email = $_SESSION['user_email'];

function _load_users() {
    $file = DATA_DIR . 'users.json';
    return file_exists($file) ? json_decode(file_get_contents($file), true) : [];
}

function _save_users($users) {
    $file = DATA_DIR . 'users.json';
    $tmp = $file . '.tmp';
    file_put_contents($tmp, json_encode($users, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX);
    rename($tmp, $file);
}

$users = _load_users();
$user = $users[$email] ?? null;

if (!$user) {
    unset($_SESSION['user_email']);
    header('Location: /');
    exit;
}

$message = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['unlink_provider'])) {
    $provider = $_POST['unlink_provider'];
    
    if (isset($user['providers'][$provider])) {
        if (count($user['providers']) > 1) {
            unset($users[$email]['providers'][$provider]);
            _save_users($users);
            // Replace placeholder {provider} dynamically using PHP str_replace
            $msg = t('Settings', 'messages.unlink_success', '{provider} has been successfully unlinked.');
            $_SESSION['flash_message'] = str_replace('{provider}', ucfirst($provider), $msg);
        } else {
            $_SESSION['flash_error'] = t('Settings', 'messages.unlink_error', 'You cannot unlink your only login method.');
        }
    }
    header('Location: /Auth/settings.php');
    exit;
}

$message = $_SESSION['flash_message'] ?? '';
$error = $_SESSION['flash_error'] ?? '';
unset($_SESSION['flash_message'], $_SESSION['flash_error']);

$providers = $user['providers'] ?? [];
$has_github = isset($providers['github']);
$has_google = isset($providers['google']);

$page_title = t('Settings', 'page_title', 'Account Settings - OmniBoard Studio');
include __DIR__ . '/../Head.php'; 
?>
<!DOCTYPE html>
<html lang="<?= htmlspecialchars($current_lang ?? 'en') ?>">
<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include __DIR__ . '/../Navbar.php'; ?>

    <main class="w-full py-12 flex-grow">
        <div class="max-w-3xl mx-auto px-6">
            <h1 class="text-3xl font-bold mb-8 text-white"><?= t('Settings', 'header.title', 'Account Settings') ?></h1>

            <?php if ($message): ?>
                <div class="bg-green-900/40 border border-green-700 text-green-300 px-4 py-3 rounded-lg mb-6">
                    <?= htmlspecialchars($message) ?>
                </div>
            <?php endif; ?>

            <?php if ($error): ?>
                <div class="bg-red-900/40 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6">
                    <?= htmlspecialchars($error) ?>
                </div>
            <?php endif; ?>

            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-8 shadow-sm">
                <div class="flex items-center gap-4 mb-4">
                    <?php if (!empty($user['avatar_url'])): ?>
                        <img src="<?= htmlspecialchars($user['avatar_url']) ?>" alt="Avatar" class="w-16 h-16 rounded-full border-2 border-slate-600">
                    <?php else: ?>
                        <div class="w-16 h-16 rounded-full bg-slate-700 flex items-center justify-center text-2xl text-slate-400 font-bold border-2 border-slate-600">
                            <?= strtoupper(substr($email, 0, 1)) ?>
                        </div>
                    <?php endif; ?>
                    <div>
                        <h2 class="text-xl font-semibold text-slate-100"><?= t('Settings', 'profile.title', 'Primary Account') ?></h2>
                        <p class="text-slate-400 text-sm"><?= htmlspecialchars($email) ?></p>
                    </div>
                </div>
                <div class="text-sm text-slate-500">
                    <p><?= t('Settings', 'profile.member_since', 'Member since:') ?> <span class="text-slate-300"><?= date('F j, Y', strtotime($user['registered_at'])) ?></span></p>
                </div>
            </div>

            <h3 class="text-xl font-semibold mb-4 text-slate-200"><?= t('Settings', 'login_methods.title', 'Connected Login Methods') ?></h3>
            <div class="space-y-4">
                
                <div class="bg-slate-800 border border-slate-700 rounded-xl p-5 flex items-center justify-between">
                    <div>
                        <p class="font-semibold text-slate-200"><?= t('Settings', 'login_methods.google.name', 'Google') ?></p>
                        <?php if ($has_google): ?>
                            <p class="text-sm text-slate-400"><?= t('Settings', 'login_methods.google.connected_as', 'Connected as') ?> <?= htmlspecialchars($providers['google']['email']) ?></p>
                        <?php else: ?>
                            <p class="text-sm text-slate-500"><?= t('Settings', 'login_methods.google.not_connected', 'Not connected') ?></p>
                        <?php endif; ?>
                    </div>
                    <div>
                        <?php if ($has_google): ?>
                            <form method="POST" class="inline">
                                <input type="hidden" name="unlink_provider" value="google">
                                <button type="submit" class="bg-slate-700 hover:bg-red-900/50 hover:text-red-400 hover:border-red-800 border border-transparent text-slate-300 px-4 py-2 rounded transition-colors text-sm font-medium"><?= t('Settings', 'login_methods.google.button_unlink', 'Unlink') ?></button>
                            </form>
                        <?php else: ?>
                            <a href="/Auth/login.php?provider=google" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded transition-colors text-sm font-medium"><?= t('Settings', 'login_methods.google.button_connect', 'Connect Google') ?></a>
                        <?php endif; ?>
                    </div>
                </div>

                <div class="bg-slate-800 border border-slate-700 rounded-xl p-5 flex items-center justify-between">
                    <div>
                        <p class="font-semibold text-slate-200"><?= t('Settings', 'login_methods.github.name', 'GitHub') ?></p>
                        <?php if ($has_github): ?>
                            <p class="text-sm text-slate-400"><?= t('Settings', 'login_methods.github.connected_as', 'Connected as') ?> <?= htmlspecialchars($providers['github']['github_username'] ?? $providers['github']['email']) ?></p>
                        <?php else: ?>
                            <p class="text-sm text-slate-500"><?= t('Settings', 'login_methods.github.not_connected', 'Not connected') ?></p>
                        <?php endif; ?>
                    </div>
                    <div>
                        <?php if ($has_github): ?>
                            <form method="POST" class="inline">
                                <input type="hidden" name="unlink_provider" value="github">
                                <button type="submit" class="bg-slate-700 hover:bg-red-900/50 hover:text-red-400 hover:border-red-800 border border-transparent text-slate-300 px-4 py-2 rounded transition-colors text-sm font-medium"><?= t('Settings', 'login_methods.github.button_unlink', 'Unlink') ?></button>
                            </form>
                        <?php else: ?>
                            <a href="/Auth/login.php?provider=github" class="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded border border-slate-600 transition-colors text-sm font-medium"><?= t('Settings', 'login_methods.github.button_connect', 'Connect GitHub') ?></a>
                        <?php endif; ?>
                    </div>
                </div>

            </div>
        </div>
    </main>

    <?php include __DIR__ . '/../Footer.php'; ?>
</body>
</html>