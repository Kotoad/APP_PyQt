<!DOCTYPE html>
<html lang="<?php echo htmlspecialchars($current_lang); ?>">

<?php $page_title = $texts['main_page_title'] ?? 'OmniBoard Studio'; include 'Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include 'Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-5xl font-extrabold tracking-tight text-white mb-6">
            <?php echo $texts['main_heading'] ?? 'Welcome to OmniBoard Studio'; ?>
        </h1>
        <p class="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
            <?php echo $texts['main_subheading'] ?? 'Build and compile MicroPython and Python projects seamlessly. A complete visual node environment with built-in code editing for Raspberry Pi Pico and more.'; ?>
        </p>
        <div class="flex justify-center gap-4">
            <a href="/Download.php"
                class="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-500 shadow-sm transition-all">
                <?php echo $texts['download_button'] ?? 'Download Now'; ?>
            </a>
            <a href="/Tutorials.php"
                class="bg-slate-800 border border-slate-700 text-slate-200 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-slate-700 transition-all">
                <?php echo $texts['read_documentation'] ?? 'Read Documentation'; ?>
            </a>
        </div>
    </header>

    <main class="w-full py-20 flex-grow">
        <section id="features" class="bg-slate-900 py-20 border-t border-slate-800">
            <div class="max-w-5xl mx-auto px-6">
                <h2 class="text-3xl font-bold mb-12 text-center text-white"><?php echo $texts['features_heading'] ?? 'Core Features'; ?></h2>
                <div class="grid md:grid-cols-3 gap-8">
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400"><?php echo $texts['feature_1_title'] ?? 'Visual Node Editor'; ?></h3>
                        <p class="text-slate-400"><?php echo $texts['feature_1_description'] ?? 'Drag and drop logic blocks, timers, and hardware interfaces to build complex logic without writing syntax manually.'; ?></p>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400"><?php echo $texts['feature_2_title'] ?? 'Integrated Compiler'; ?></h3>
                        <p class="text-slate-400"><?php echo $texts['feature_2_description'] ?? 'Instantly translate visual node graphs into optimized MicroPython and Python code ready for deployment to connected devices.'; ?></p>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400"><?php echo $texts['feature_3_title'] ?? 'Hardware Support'; ?></h3>
                        <p class="text-slate-400"><?php echo $texts['feature_3_description'] ?? 'Native support and setup workflows for the Raspberry Pi Pico series and Raspberry Pi 1 to 5.'; ?></p>
                    </div>
                </div>
                <h2 class="text-3xl font-bold mt-20 mb-12 text-center text-white"><?php echo $texts['future_developments_heading'] ?? 'Future Developments'; ?></h2>
                <div class="grid md:grid-cols-3 gap-8">
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400"><?php echo $texts['future_development_1_title'] ?? 'Expanded Hardware Support'; ?></h3>
                        <p class="text-slate-400"><?php echo $texts['future_development_1_description'] ?? 'Adding compatibility with more microcontroller platforms and single-board computers beyond the Raspberry Pi ecosystem.'; ?></p>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400"><?php echo $texts['future_development_2_title'] ?? 'Advanced Node Types'; ?></h3>
                        <p class="text-slate-400"><?php echo $texts['future_development_2_description'] ?? 'Introducing new node categories for more complex logic, data processing, and hardware interactions.'; ?></p>
                    </div>
                    <div class="p-6 border border-slate-700 rounded-xl shadow-sm bg-slate-800">
                        <h3 class="text-xl font-bold mb-3 text-blue-400"><?php echo $texts['future_development_3_title'] ?? 'Community Contributions'; ?></h3>
                        <p class="text-slate-400"><?php echo $texts['future_development_3_description'] ?? 'Encouraging users to share their own node templates, tutorials, and project ideas to foster a collaborative learning environment.'; ?></p>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <?php include 'Footer.php'; ?>

</body>

</html>