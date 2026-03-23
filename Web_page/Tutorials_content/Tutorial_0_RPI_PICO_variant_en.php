<!DOCTYPE html>
<html lang="<?php echo htmlspecialchars($current_lang); ?>">

<?php $page_title = $texts['rpi_pico_setup_title']; include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?php echo htmlspecialchars($texts['rpi_pico_setup_title']); ?>
        </h1>
        <p class="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
            <?php echo htmlspecialchars($texts['rpi_pico_setup_description']); ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['rpi_pico_setup_supported_variants']); ?></h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                    class="p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Pico</div>
                <div
                    class="p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Pico W*</div>
                <div
                    class="p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Pico WH*</div>
                <div
                    class="p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Pico 2</div>
                <div
                    class="p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-sm font-medium text-center">
                    Raspberry Pi Pico 2 W*</div>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['rpi_pico_setup_you_will_need_title']); ?></h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['rpi_pico_setup_you_will_need_description']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['rpi_pico_setup_you_will_need_micro_usb']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['rpi_pico_setup_you_will_need_computer']); ?></span>
                </li>
            </ul>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['rpi_pico_setup_steps_title']); ?></h2>
            <ul class="space-y-4">
                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        1</div>
                    <div class="w-full">
                        <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['rpi_pico_setup_steps_step_1']); ?></div>
                        <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['rpi_pico_setup_steps_step_1_description']); ?><br class="sm:hidden"> <a
                                        href="https://micropython.org/download/RPI_PICO/"
                                        class="text-blue-400 hover:text-blue-300 underline break-all">https://micropython.org/download/RPI_PICO/</a></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['rpi_pico_setup_steps_step_1_w_description']); ?><br class="sm:hidden"> <a
                                        href="https://micropython.org/download/RPI_PICO_W/"
                                        class="text-blue-400 hover:text-blue-300 underline break-all">https://micropython.org/download/RPI_PICO_W/</a></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['rpi_pico_setup_steps_step_1_2_description']); ?><br class="sm:hidden"> <a
                                        href="https://micropython.org/download/RPI_PICO2/"
                                        class="text-blue-400 hover:text-blue-300 underline break-all">https://micropython.org/download/RPI_PICO2/</a></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['rpi_pico_setup_steps_step_1_2_w_description']); ?><br class="sm:hidden"> <a
                                        href="https://micropython.org/download/RPI_PICO2_W/"
                                        class="text-blue-400 hover:text-blue-300 underline break-all">https://micropython.org/download/RPI_PICO2_W/</a></span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        2</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['rpi_pico_setup_steps_step_2']); ?></div>
                </div>
                <div class="flex gap-4 p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        3</div>
                    <div class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['rpi_pico_setup_steps_step_3']); ?></div>
                </div>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>

</body>

</html>