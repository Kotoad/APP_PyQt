<!DOCTYPE html>
<html lang="<?php echo htmlspecialchars($current_lang); ?>">

<?php $page_title = $texts['led_traffic_light_title']; include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php';?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center border-b border-slate-800">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?php echo htmlspecialchars($texts['led_traffic_light_title']); ?>
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto"></p>
            <?php echo htmlspecialchars($texts['led_traffic_light_description']); ?>
        </p>
    </header>

    <hr class="border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['led_traffic_light_steps_title']); ?></h2>
            <div class="space-y-4">
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        1</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['led_traffic_light_step_1']); ?></p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        2</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['led_traffic_light_step_2']); ?></p>
                    <p class="text-slate-300 mt-1">
                        <?php echo htmlspecialchars($texts['led_traffic_light_step_2_hint']); ?>
                    </p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            <?php echo htmlspecialchars($texts['led_traffic_light_step_2_hint_solution']); ?>
                            <span
                                class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                        </summary>
                        <ul 
                            class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span>
                                    <?php echo htmlspecialchars($texts['led_traffic_light_step_2_hint_solution_1']); ?>
                                </span>
                            </li>
                        </ul>
                    </details>
                </div>
        </section>
    </main>


</body>

</html>