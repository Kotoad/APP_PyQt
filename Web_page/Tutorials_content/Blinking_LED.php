<!DOCTYPE html>
<html lang="<?php echo htmlspecialchars($current_lang); ?>">

<?php $pageTitle = $texts['blinking_led_title']; include '../Head.php'; ?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?php echo htmlspecialchars($texts['blinking_led_title']); ?>
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto">
            <?php echo htmlspecialchars($texts['blinking_led_description']); ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['blinking_led_steps_title']); ?></h2>
            <div class="space-y-4">
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        1</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['blinking_led_step_1']); ?></p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        2</div>
                    <p class="text-slate-300 mt-1 py-2"><?php echo htmlspecialchars($texts['blinking_led_step_2']); ?></p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            <?php echo htmlspecialchars($texts['blinking_led_step_2_hint']); ?>
                            <span
                                class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                        </summary>
                        <ul
                            class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['blinking_led_step_2_solution_1']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['blinking_led_step_2_solution_2']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['blinking_led_step_2_solution_3']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['blinking_led_step_2_solution_4']); ?></span>
                            </li>
                        </ul>
                        <figure class="w-full flex flex-col items-center mt-4">
                            <img src="Blinking_LED/Blinking_LED_Flowchart.png" alt="Blinking LED Blocks"
                                class="rounded-lg border border-slate-700">
                            <figcaption class="text-sm text-slate-500 mt-2"><?php echo htmlspecialchars($texts['blinking_led_step_2_caption']); ?></figcaption>
                        </figure>
                    </details>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        3</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['blinking_led_step_3']); ?></p>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span><?php echo htmlspecialchars($texts['blinking_led_step_3_solution_1']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span><?php echo htmlspecialchars($texts['blinking_led_step_3_solution_2']); ?></span>
                        </li>
                    </ul>
                    <figure class="w-full flex flex-col items-center mt-4">
                        <img src="Blinking_LED/Blinking_LED_Circuit.png" alt="Blinking LED Circuit"
                            class="rounded-lg border border-slate-700">
                        <figcaption class="text-sm text-slate-500 mt-2"><?php echo htmlspecialchars($texts['blinking_led_step_3_caption']); ?>
                        </figcaption>
                    </figure>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        4</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['blinking_led_step_4']); ?></p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        5</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['blinking_led_step_5']); ?></p>
                </div>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['blinking_led_bonus_info_title']); ?></h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['blinking_led_bonus_info_1_title']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['blinking_led_bonus_info_2_title']); ?></span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
import machine # Needed for controlling the GPIO pins
import time # Needed for creating delays
led = machine.Pin(2, machine.Pin.OUT) # Asign GPIO pin 2 to control the LED as and output
while True: # Create an infinite loop to keep the LED blinking
    togle(led) # Toggle the LED on and off.
                 This is a custom function that would be generated by the blocks. 
                 It would turn the LED on if it's currently off, and turn it off if it's currently on.
    time.sleep(1) # Wait for 1 second before toggling again
                </code></pre>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['blinking_led_bonus_info_3_title']); ?></span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
import time # Needed for creating delays
import RPi.GPIO as GPIO # Needed for controlling the GPIO pins
GPIO.setmode(GPIO.BCM) # Set the GPIO mode to BCM
GPIO.setup(2, GPIO.OUT) # Asign GPIO pin 2 to control the LED as and output
while True: # Create an infinite loop to keep the LED blinking
    togle(pin=2) # Toggle the LED on and off.
                   This is a custom function that would be generated by the blocks. 
                   It would turn the LED on if it's currently off, and turn it off if it's currently on.
    time.sleep(1) # Wait for 1 second before toggling again
                </code></pre>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['blinking_led_bonus_info_4_title']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['blinking_led_bonus_info_4_description']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['blinking_led_bonus_info_5_title']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span>
                        <?php echo htmlspecialchars($texts['blinking_led_bonus_info_5_description']); ?>
                    </span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['blinking_led_bonus_info_6_title']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['blinking_led_bonus_info_6_description']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['blinking_led_bonus_info_7_title']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['blinking_led_bonus_info_7_description']); ?></span>
                </li>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>

</body>

</html>