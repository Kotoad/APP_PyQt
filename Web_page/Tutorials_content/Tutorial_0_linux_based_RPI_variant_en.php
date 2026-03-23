<!DOCTYPE html>
<html lang="<?php echo htmlspecialchars($current_lang); ?>">

<?php $pageTitle = $texts['linux_rpi_setup_title']; include '../Head.php'; ?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center border-b border-slate-800">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?php echo htmlspecialchars($texts['linux_rpi_setup_title']); ?>
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto">
            <?php echo htmlspecialchars($texts['linux_rpi_setup_description']); ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['linux_rpi_models_title']); ?></h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 5</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 4 Model B</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 3 Model B+</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 3 Model B</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 3 Model A+</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 2 Model B</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 1 Model B+</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 1 Model B</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 1 Model A+</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi 1 Model A</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Zero 2 W*</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Zero 2 WH*</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Zero W*</div>
                <div
                    class="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Zero</div>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['linux_rpi_setup_you_will_need_title']); ?></h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['linux_rpi_setup_you_will_need_description']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['linux_rpi_setup_you_will_need_microsd']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['linux_rpi_setup_you_will_need_power_supply']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['linux_rpi_setup_you_will_need_hdmi']); ?></span>
                </li>
            </ul>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_title']); ?></h2>
            <div class="space-y-4">

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        1</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_description']); ?><a href="https://www.raspberrypi.com/software/"
                            class="text-blue-400 hover:text-blue-300 underline">https://www.raspberrypi.com/software/</a>.
                    </div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        2</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_2']); ?></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        3</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_3']); ?></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        4</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_4']); ?></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        5</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_5']); ?></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        6</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_6']); ?></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        7</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_7']); ?></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        8</div>
                    <div class="text-slate-300 mt-1"><strong class="text-white"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_8']); ?></strong></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        9</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_9']); ?></div>
                        <strong class="text-white"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_9_highlight']); ?></strong></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        10</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_10']); ?></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        11</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_11']); ?></div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        12</div>
                    <div class="text-slate-300 mt-1">
                        <span class="font-bold text-white"><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12']); ?></span>
                        <ul class="mt-4 space-y-3 pl-4 border-l-2 border-slate-700">
                            <li class="relative">
                                <span class="absolute -left-[21px] top-2 w-2 h-2 rounded-full bg-slate-600"></span>
                                <span><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12_hint']); ?></span>
                            </li>
                            <li class="relative">
                                <span class="absolute -left-[21px] top-2 w-2 h-2 rounded-full bg-slate-600"></span>
                                <span><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12_hint_solution']); ?></span>
                                <code
                                    class="bg-slate-900 text-sky-400 px-1 py-0.5 rounded border border-slate-700">ssh username@ip_address</code>.
                                <span><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12_hint_solution_2']); ?></span>
                            </li>
                            <li class="relative">
                                <span class="absolute -left-[21px] top-2 w-2 h-2 rounded-full bg-slate-600"></span>
                                <span><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12_hint_solution_3']); ?></span>
                                <code
                                    class="bg-slate-900 text-sky-400 px-1 py-0.5 rounded border border-slate-700">sudo apt update && sudo apt full-upgrade -y</code>
                            </li>
                            <li class="relative">
                                <span class="absolute -left-[21px] top-2 w-2 h-2 rounded-full bg-slate-600"></span>
                                <span><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12_hint_solution_4']); ?></span>
                            </li>
                            <li class="relative">
                                <span class="absolute -left-[21px] top-2 w-2 h-2 rounded-full bg-slate-600"></span>
                                <span><?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12_hint_solution_5']); ?></span>
                                <code
                                    class="bg-slate-900 text-sky-400 px-1 py-0.5 rounded border border-slate-700">sudo reboot</code>.
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="mt-8 p-4 bg-blue-900/20 border border-blue-800 rounded-lg text-blue-200 text-sm">
                <?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12_additional_info']); ?>
            </div>
            <div class="mt-8 p-4 bg-blue-900/20 border border-blue-800 rounded-lg text-blue-200 text-sm">
                <?php echo htmlspecialchars($texts['linux_rpi_setup_steps_step_12_additional_info_2']); ?>
            </div>
        </section>
    </main>

    <?php include '../Footer.php'; ?>

</body>

</html>