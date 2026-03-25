<?php require_once '../i18n.php';?>

<!DOCTYPE html>
<html lang="<?= htmlspecialchars($current_lang ?? 'en') ?>">
<?php
$page_title = t('Login', 'page_title', 'Login - OmniBoard Studio');
include '../Head.php';
?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <main class="flex-grow flex items-center justify-center">
        <div class="bg-slate-800 border border-slate-700 rounded-lg p-8 w-full max-w-md">
            <h1 class="text-2xl font-bold mb-6 text-center text-white"><?= t('Login', 'header', 'Login to Your Account') ?></h1>
            <div class="space-y-4">
                <a href="login.php?provider=github" class="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded flex items-center justify-center gap-2 transition-colors">
                    <img src="/assets/github_icon.png" alt="GitHub" class="w-5 h-5">
                    <?= t('Login', 'github_button', 'Continue with GitHub') ?>
                </a>
                <a href="login.php?provider=google" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 px-4 rounded flex items-center justify-center gap-2 transition-colors">
                    <img src="/assets/google_icon.png" alt="Google" class="w-5 h-5">
                    <?= t('Login', 'google_button', 'Continue with Google') ?>
                </a>
            </div>
        </div>
    </main>

    <?php include '../Footer.php'; ?>