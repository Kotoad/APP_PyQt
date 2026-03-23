<!DOCTYPE html>
<html lang="<?php echo htmlspecialchars($current_lang); ?>">

<?php $page_title = $texts['timing_led_title']; include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 class="text-4xl font-bold mb-6 text-white"><?php echo htmlspecialchars($texts['timing_led_title']); ?></h1>
        <p class="text-slate-400 text-xl mb-10 max-w-2xl mx-auto"><?php echo htmlspecialchars($texts['timing_led_description']); ?></p>
    </header>

    <hr class="border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['timing_led_steps_title']); ?></h2>
            <div class="space-y-4">
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        1</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['timing_led_step_1']); ?></p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        2</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['timing_led_step_2']); ?></p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            <?php echo htmlspecialchars($texts['timing_led_step_2_hint']); ?>
                            <span
                                class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                        </summary>
                        <ul
                            class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_2_hint_solution_1']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_2_hint_solution_2']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_2_hint_solution_3']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_2_hint_solution_4']); ?></span>
                            </li>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_2_hint_solution_5']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_2_hint_solution_6']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_2_hint_solution_7']); ?></span>
                            </li>
                        </ul>
                    </details>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        3</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['timing_led_step_3']); ?></p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            <?php echo htmlspecialchars($texts['timing_led_step_3_hint']); ?>
                            <span
                                class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                        </summary>
                        <ul
                            class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_3_hint_solution_1']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['timing_led_step_3_hint_solution_2']); ?></span>
                            </li>
                            <figure class="w-full flex flex-col items-center mt-4">
                                <img src="Blinking_LED/Blinking_LED_Circuit.png" alt="Timind LED circiut"
                                    class="rounded-lg border border-slate-700">
                                <figcaption class="text-sm text-slate-500 mt-2"><?php echo htmlspecialchars($texts['timing_led_step_3_hint_solution_3']); ?></figcaption>
                            </figure>
                        </ul>
                    </details>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        4</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['timing_led_step_4']); ?></p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        5</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['timing_led_step_5']); ?></p>
                </div>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['timing_led_bonus_info_title']); ?></h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['timing_led_bonus_info_code_example']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['timing_led_bonus_info_code_description']); ?></span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
from machine import Pin # Import the Pin class to control GPIO pins
import time # Import the time module for timing functions
led = Pin(15, Pin.OUT) # Set GPIO pin 15 as an output for the LED
while True: # Start an infinite loop
    led.value(1) # Turn the LED on
    time.sleep(1) # Wait for 1 second
    led.value(0) # Turn the LED off
    time.sleep(1) # Wait for 1 second
                </code></pre>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['timing_led_bonus_info_python_code']); ?></span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
import RPi.GPIO as GPIO # Import the RPi.GPIO library to control GPIO pins
import time # Import the time module for timing functions
GPIO.setmode(GPIO.BCM) # Set the GPIO mode to BCM
GPIO.setup(15, GPIO.OUT) # Set GPIO pin 15 as an output for the LED
while True: # Start an infinite loop
    GPIO.output(15, GPIO.HIGH) # Turn the LED on
    time.sleep(1) # Wait for 1 second
    GPIO.output(15, GPIO.LOW) # Turn the LED off
    time.sleep(1) # Wait for 1 second
                </code></pre>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>

</body>

</html>