<!DOCTYPE html>
<html lang="<?php echo htmlspecialchars($current_lang); ?>">

<?php $page_title = $texts['basic_terms_title']; include '../Head.php';?>

<body class="bg-slate-900 text-slate-100 font-sans antialiased min-h-screen flex flex-col">

    <?php include '../Navbar.php'; ?>

    <header class="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-white mb-6">
            <?php echo htmlspecialchars($texts['basic_terms_title']); ?>
        </h1>
        <p class="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
            <?php echo htmlspecialchars($texts['basic_terms_description']); ?>
        </p>
    </header>

    <hr class=" border-t border-slate-800">

    <main class="max-w-4xl mx-auto px-6 py-12 space-y-16 flex-grow">
        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['basic_terms_section_title']); ?></h2>
            <p class="text-slate-300 mb-4"><?php echo htmlspecialchars($texts['basic_terms_section_description']); ?></p>
            <p class="text-slate-300 mb-4"><?php echo htmlspecialchars($texts['basic_terms_section_content']); ?></p>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['basic_terms_electric_quantities']); ?></span>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_charge']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_charge_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_voltage']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_voltage_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_current']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_current_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_resistance']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_resistance_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_power']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_power_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_conductance']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_conductance_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_energy']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_energy_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_capacity']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_capacity_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_electric_inductance']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_electric_inductance_description']); ?></span>
                        </li>
                    </ul>
                </li>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1">●</span>
                    <span><?php echo htmlspecialchars($texts['basic_terms_magnetic_quantities']); ?></span>
                    <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_magnetic_flux']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_magnetic_flux_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_magnetic_field_strength']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_magnetic_field_strength_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_magnetic_permeability']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_magnetic_permeability_description']); ?></span>
                        </li>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_magnetic_reluctance']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_magnetic_reluctance_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_magnetic_energy']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_magnetic_energy_description']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_magnetic_force']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_magnetic_force_description']); ?></span>
                        </li>
                        </li>
                        <li class="flex items-start gap-3">
                            <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_magnetic_moment']); ?></span>
                        </li>
                        <li class="flex items-start gap-3">
                            <span><?php echo htmlspecialchars($texts['basic_terms_magnetic_moment_description']); ?></span>
                        </li>
                    </ul>
                </li>
        </section>

        <section>
            <h2 class="text-2xl font-bold text-blue-400 mb-6"><?php echo htmlspecialchars($texts['basic_terms_electrical_terms']); ?></h2>
            <p class="text-slate-300 mb-4"><?php echo htmlspecialchars($texts['basic_terms_electrical_terms_description']); ?></p>
            <p class="text-slate-300 mb-4"><?php echo htmlspecialchars($texts['basic_terms_electrical_terms_subdescription']); ?></p>
            <ul class="space-y-4 text-slate-300 bg-slate-800/50 p-6 rounded-xl border border-slate-700/50">
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_ground']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['basic_terms_ground_description']); ?></span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Ground_Symbol.png" alt="Ground Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_ground_symbol_caption']); ?></figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_power_supply']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['basic_terms_power_supply_description']); ?></span>
                </li>
                <div class="w-full flex justify-center gap-12 mt-4">
                    <figure class="flex flex-col items-center">
                        <img src="Basic_therms/Power_Supply_Symbol_DC.png" alt="Power Supply Symbol DC"
                            class="max-w-full h-auto">
                        <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_power_supply_symbol_caption_dc']); ?></figcaption>
                    </figure>
                    <figure class="flex flex-col items-center">
                        <img src="Basic_therms/Power_Supply_Symbol_AC.png" alt="Power Supply Symbol AC"
                            class="max-w-full h-auto">
                        <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_power_supply_symbol_caption_ac']); ?></figcaption>
                    </figure>
                </div>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_pin_symbol']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['basic_terms_pin_symbol_description']); ?></span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Pin_Connection_Symbol.png" alt="Pin Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_pin_symbol_caption']); ?></figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_resistor']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['basic_terms_resistor_description']); ?></span>
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Resistor_Symbol.png" alt="Resistor Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_resistor_symbol_caption']); ?></figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_capacitor']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['basic_terms_capacitor_description']); ?></span>
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Capacitor_Symbol.png" alt="Capacitor Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_capacitor_symbol_caption']); ?></figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_inductor']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['basic_terms_inductor_description']); ?></span>
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Inductor_Symbol.png" alt="Inductor Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_inductor_symbol_caption']); ?></figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_diode']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span><?php echo htmlspecialchars($texts['basic_terms_diode_description']); ?></span>
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Diode_Symbol.png" alt="Diode Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_diode_symbol_caption']); ?></figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_led_diode']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span>
                        <?php echo htmlspecialchars($texts['basic_terms_led_diode_description']); ?>
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/LED_Symbol.png" alt="LED Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_led_symbol_caption']); ?></figcaption>
                </figure>
                <li class="flex items-start gap-3">
                    <span class="text-blue-500 mt-1"><?php echo htmlspecialchars($texts['basic_terms_transistor']); ?></span>
                </li>
                <li class="flex items-start gap-3">
                    <span>
                        <?php echo htmlspecialchars($texts['basic_terms_transistor_description']); ?>
                    </span>
                </li>
                <figure class="w-full flex flex-col items-center mt-4">
                    <img src="Basic_therms/Transistor_Symbol.png" alt="Transistor Symbol" class="max-w-full h-auto">
                    <figcaption class="text-xs text-slate-400 mt-1"><?php echo htmlspecialchars($texts['basic_terms_transistor_symbol_caption']); ?></figcaption>
                </figure>
            </ul>
        </section>
    </main>

    <?php include '../Footer.php'; ?>
</body>

</html>