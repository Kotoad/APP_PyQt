<!DOCTYPE html>
<html lang="<?php echo htmlspecialchars($current_lang); ?>">

<?php $pageTitle = $texts['button_led_title']; include '../Head.php'; ?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?php echo htmlspecialchars($texts['button_led_title']); ?>
        </h1>
        <p class="text-lg text-slate-400 max-w-2xl mx-auto">
            <?php echo htmlspecialchars($texts['button_led_description']); ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['button_led_steps_title']); ?></h2>
            <div class="space-y-4">
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        1</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['button_led_step_1']); ?></p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        2</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['button_led_step_2']); ?></p>
                    <details
                        class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                        <summary
                            class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                            <?php echo htmlspecialchars($texts['button_led_step_2_hint']); ?>
                            <span
                                class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                        </summary>
                        <ul
                            class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['button_led_step_2_solution_1']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['button_led_step_2_solution_2']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['button_led_step_2_solution_3']); ?></span>
                            </li>
                            <li class="flex items-start gap-3">
                                <span class="text-blue-500 mt-1">●</span>
                                <span><?php echo htmlspecialchars($texts['button_led_step_2_solution_4']); ?></span>
                            </li>
                        </ul>
                        <figure class="w-full flex flex-col items-center mt-4">
                            <img src="Button_led/Button_led_Flowchart.png" alt="Button controlled LED Blocks"
                                class="rounded-lg border border-slate-700">
                            <figcaption class="text-sm text-slate-500 mt-2"><?php echo htmlspecialchars($texts['button_led_step_2_caption']); ?></figcaption>
                        </figure>
                    </details>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        3</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['button_led_step_3']); ?></p>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span><?php echo htmlspecialchars($texts['button_led_step_3_solution_1']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1">●</span>
                            <span><?php echo htmlspecialchars($texts['button_led_step_3_solution_2']); ?></span>
                        </li>
                        <details
                            class="bg-slate-800 border border-slate-700 rounded-xl p-4 group transition-all duration-300">
                            <summary
                                class="font-bold text-white cursor-pointer list-none flex justify-between items-center">
                                <?php echo htmlspecialchars($texts['button_led_step_3_hint']); ?>
                                <span
                                    class="text-blue-400 transform group-open:rotate-180 transition-transform duration-200">▼</span>
                            </summary>

                            <ul
                                class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50 mt-4">
                                <li class="flex items-start gap-3">
                                    <span class="text-blue-500 mt-1">●</span>
                                    <span><?php echo htmlspecialchars($texts['button_led_step_3_solution_3']); ?></span>
                                </li>
                                <li class="flex items-start gap-3">
                                    <span class="text-blue-500 mt-1">●</span>
                                    <span><?php echo htmlspecialchars($texts['button_led_step_3_solution_4']); ?></span>
                                </li>
                                <figure class="w-full flex flex-col items-center mt-4">
                                    <img src="Button_led/Button_led_Circuit.png" alt="Button controlled LED Circuit"
                                        class="rounded-lg border border-slate-700">
                                    <figcaption class="text-sm text-slate-500 mt-2"><?php echo htmlspecialchars($texts['button_led_step_3_caption']); ?></figcaption>
                                </figure>
                            </ul>
                        </details>
                    </ul>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        4</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['button_led_step_4']); ?></p>
                </div>
                <div class="p-5 bg-slate-800 border border-slate-700 rounded-xl">
                    <div
                        class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold border border-blue-500/30">
                        5</div>
                    <p class="text-slate-300 mt-1"><?php echo htmlspecialchars($texts['button_led_step_5']); ?></p>
                </div>
            </div>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['button_led_bonus_info_title']); ?></h2>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['button_led_bonus_info_1']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['button_led_bonus_info_2']); ?></span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
from machine import Pin # Import the Pin class to control GPIO pins
led = Pin(2, Pin.OUT) # Set GPIO pin 2 as an output for the LED
button = Pin(0, Pin.IN, Pin.PULL_UP) # Set GPIO pin 0 as an input for the button with a pull-up resistor
while True: # Start an infinite loop
    if button.value() == 1: # Check if the button is pressed (active high)
        led.value(1) # Turn the LED on
    else: # If the button is not pressed
        led.value(0) # Turn the LED off
                </code></pre>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['button_led_bonus_info_3']); ?></span>
                </li>
                <pre class="bg-slate-800 p-4 rounded-lg overflow-x-auto mt-4 text-sm"><code class="language-python">
import RPi.GPIO as GPIO # Import the GPIO library to control GPIO pins
GPIO.setmode(GPIO.BCM) # Set the GPIO mode to BCM
GPIO.setup(2, GPIO.OUT) # Set GPIO pin 2 as an output for the LED
GPIO.setup(0, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set GPIO pin 0 as an input for the button with a pull-up resistor
while True: # Start an infinite loop
    if GPIO.input(0) == GPIO.HIGH: # Check if the button is pressed (active high)
        GPIO.output(2, GPIO.HIGH) # Turn the LED on
    else: # If the button is not pressed
        GPIO.output(2, GPIO.LOW) # Turn the LED off
                </code></pre>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>

</body>

</html>