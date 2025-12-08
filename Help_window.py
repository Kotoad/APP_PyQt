from Imports import (QDialog, Qt, QVBoxLayout, QLabel, QTabWidget, QWidget, QFont, QTextEdit,
                     QScrollArea, QPushButton, os)


class HelpWindow(QDialog):
    """Singleton Help Window"""
    _instance = None

    def __init__(self, parent=None, which=0):
        super().__init__(None)
        self.parent_canvas = parent
        self.which = which
        
        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent, which):
        """Get or create singleton instance"""
        if cls._instance is None or not cls._instance.isVisible():
            cls._instance = cls(parent, which)
        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Help")
        self.resize(600, 400)
        
        self.setWindowFlags(Qt.WindowType.Window)
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QTabWidget::pane {
                border: 1px solid #3A3A3A;
                background-color: #2B2B2B;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #1F1F1F;
                color: #FFFFFF;
                padding: 8px 20px;
                border: 1px solid #3A3A3A;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1F538D;
            }
            QTabBar::tab:hover {
                background-color: #2667B3;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: none;
                padding: 10px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #1F538D;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.create_getting_started_tab()
        self.create_examples_tab()
        self.create_faq_tab()
        
        self.tab_widget.setCurrentIndex(self.which)
        
    def create_getting_started_tab(self):
        """Create the Getting Started tab"""
        print("Creating Getting Started tab")
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml("""
            <h2 style="color:#FFFFFF;">Getting Started</h2>
            <p>Welcome to the Help Window! Here you can find information to get started with the application.</p>
            <h3 style="color:#FFFFFF;">Features:</h3>
            <ul>
                <li>Feature 1: Description of feature 1.</li>
                <li>Feature 2: Description of feature 2.</li>
                <li>Feature 3: Description of feature 3.</li>
            </ul>
            <h3 style="color:#FFFFFF;">Tips:</h3>
            <ol>
                <li>Tip 1: Description of tip 1.</li>
                <li>Tip 2: Description of tip 2.</li>
                <li>Tip 3: Description of tip 3.</li>
            </ol>
            <p>For more detailed information, please refer to the FAQ tab.</p>
        """)
        
        layout.addWidget(text_edit)
        print("Added label to Getting Started tab")
        self.tab_widget.addTab(tab, "Getting Started")

    def create_examples_tab(self):
        """Create the Examples tab with scrollable vertical examples"""
        print("Creating Examples tab")
        self.examples_tab = QWidget()
        self.examples_layout = QVBoxLayout(self.examples_tab)
        self.examples_layout.setContentsMargins(0, 0, 0, 0)
        
        self.show_examples_list()
        
        self.tab_widget.addTab(self.examples_tab, "Examples")
        print("Added scrollable examples to Examples tab")

    def show_examples_list(self):
        """Show the examples list view"""
        # Clear layout
        while self.examples_layout.count():
            self.examples_layout.takeAt(0).widget().deleteLater()
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #2B2B2B; }
            QScrollBar:vertical { background-color: #1F1F1F; width: 12px; border: none; }
            QScrollBar::handle:vertical { background-color: #3A3A3A; border-radius: 6px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background-color: #4A4A4A; }
        """)
        
        # Create container widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add examples
        examples = [
            ("Example 1: Blinking LED", "Create basic blinking LED.", "1"),
            ("Example 2: If Statement", "Learn how to use conditional logic in your diagrams.", "2"),
            ("Example 3: Loops", "Understand how to create repeating processes.", "3"),
            ("Example 4: Complex Logic", "Combine multiple elements for advanced workflows.", "4"),
            ("Example 5: Data Processing", "Process input/output in your flowcharts.", "5"),
        ]
        
        for title, description, example_id in examples:
            item_widget = self._create_example_item(title, description, example_id)
            scroll_layout.addWidget(item_widget)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        self.examples_layout.addWidget(scroll)
    
    def _create_example_item(self, title, description, example_id):
        """Helper method to create a styled example item"""
        item = QWidget()
        item_layout = QVBoxLayout(item)
        item_layout.setContentsMargins(10, 10, 10, 10)
        item_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1F538D;")
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #CCCCCC;")
        
        view_btn = QPushButton("View Example")
        view_btn.setMaximumWidth(120)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        view_btn.clicked.connect(lambda: self.show_example_detail(title, description, example_id))
        
        item_layout.addWidget(title_label)
        item_layout.addWidget(desc_label)
        item_layout.addWidget(view_btn)
        
        item.setStyleSheet("QWidget { border-bottom: 1px solid #3A3A3A; }")
        return item

    def show_example_detail(self, title, description, example_id):
        """Show detailed view of an example"""
        self.current_example = (title, description)
        
        # Clear layout
        while self.examples_layout.count():
            self.examples_layout.takeAt(0).widget().deleteLater()
        
        # Create detail view
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(10, 10, 10, 10)
        detail_layout.setSpacing(10)
        
        # Back button
        back_btn = QPushButton("← Back to Examples")
        back_btn.setMaximumWidth(150)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.show_examples_list)
        detail_layout.addWidget(back_btn)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1F538D;")
        detail_layout.addWidget(title_label)
        
        # Content area (replace with your actual content)
        content = QTextEdit()
        content.setReadOnly(True)
        self.fill_content_area(content, example_id)
        detail_layout.addWidget(content)
        
        # Add to tab
        self.examples_layout.addWidget(detail_widget)

    def fill_content_area(self, content, example_id):
        match example_id:
            case "1":
                css = self.get_content_stylesheet()
                current_dir = os.path.dirname(os.path.abspath(__file__))
                Blinking_LED_Diagram = os.path.join(current_dir, "resources", "images", "Blinking_LED", "blinking_led_diagram.png")
                Blinking_LED_Diagram = os.path.abspath(Blinking_LED_Diagram)  # Convert to absolute path
                Blinking_LED_Diagram = Blinking_LED_Diagram.replace("\\", "/")
                Blinking_LED_Flowchart = os.path.join(current_dir, "resources", "images", "Blinking_LED", "blinking_led_flowchart.png")
                Blinking_LED_Flowchart = os.path.abspath(Blinking_LED_Flowchart)
                Blinking_LED_Flowchart = Blinking_LED_Flowchart.replace("\\", "/")
                print(f"Image path for help content: {Blinking_LED_Diagram}")
                content.setHtml(
                    f"""
                        {css}
                        <p>
                            Goal of this example is to demonstrate how to create a blinking LED using basic flowchart elements.<br>
                        </p>
                        <h2>You will need:</h2>
                        <ul>
                            <li>Any Raspberry Pi board</li>
                            <li>USB cable to connect the board to your computer</li>
                            <li>Any LED</li>
                            <li>220 Ohm resistor</li>
                            <li>Breadboard and jumper wires</li>
                        </ul>
                        <h2>Wiring Diagram:</h2>
                        <div align="left">
                            <img src="{Blinking_LED_Diagram}" style="max-width: 100%; height: auto; image-rendering: crisp-edges;" />
                        </div>
                        <h2>How to make it work:</h2>
                        <p>
                            <h3>The flowchart will consists of the following elements:</h3>
                            <ul>
                                <li><span class="highlight">1x Start</span>: Initializes the program.</li>
                                <li><span class="highlight">2x Switch</span>: Controls the LED state (ON/OFF).</li>
                                <li><span class="highlight">2x Wait</span>: Introduces delays for blinking effect.</li>
                                <li><span class="highlight">1x End</span>: Terminates the program.</li>
                            </ul>
                            <h3>Flowchart Logic:</h3>
                            <ol>
                                <li>The program starts with the <span class="code">Start</span> element.</li>
                                <li>It then enters a loop where it turns the LED ON using the first <span class="code">Switch</span> element.</li>
                                <li>The program waits for 1 second using the first <span class="code">Wait</span> element.</li>
                                <li>Next, it turns the LED OFF using the second <span class="code">Switch</span> element.</li>
                                <li>It waits for another 1 second using the second <span class="code">Wait</span> element.</li>
                                <li>This loop continues indefinitely until the program is manually stopped or terminated using the <span class="code">End</span> element.</li>
                            </ol>
                            <h3>Creating the Flowchart:</h3>
                            <ol>
                                <li>Create new varible by clicking the "Variables" button in the main window toolbar.</br>Name it <span class="highlight">however u want</span> and set its type to <span class="highlight">Boolean</span>.</li>
                                <li>Create new device by clicking the "Devices" button in the main window toolbar.</br>Name it <span class="highlight">LED</span> for convenience and set its type to <span class="highlight">Output</span>.</li>
                                <li>To add new elements to the canvas, click the "Elements" button in the main window toolbar, then click "add Element".</li>
                                <li>Select the required elements from the list and place them on the canvas.</li>
                                <li>Connect the elements in the following order:</br>
                                    <ul>
                                        <li>"<span class="code">Start → While</span>", make sure to set the condition to <span class="code">True</span> to create an infinite loop.</li>
                                        <li>"<span class="code">While</span> (Connect to top connection point) <span class="code">→ Switch</span> (LED ON)"</li>
                                        <li>"<span class="code">While</span> (Connect to bottom connection point) <span class="code">→ End</span>"</li>
                                        <li>"<span class="code">Switch</span> (LED ON) <span class="code">→ Wait</span> (1s)", this will keep the LED on for 1 second.</li>
                                        <li>"<span class="code">Wait</span> (1s) <span class="code">→ Switch</span> (LED OFF)", this will turn the LED off.</li>
                                        <li>"<span class="code">Switch</span> (LED OFF) <span class="code">→ Wait</span> (1s)", this will keep the LED off for 1 second.</li>
                                        <li>"<span class="code">Wait</span> (1s) <span class="code">→ End</span>", always make sure to properly terminate the program.</li>
                                    </ul>
                                </li>
                            </ol>
                            <h3>Flowchart Diagram:</h3>
                            <div align="left">
                                <img src="{Blinking_LED_Flowchart}" style="max-width: 100%; height: auto; image-rendering: crisp-edges;" />   
                        </p>  
                    """)
            case "2":
                css = self.get_content_stylesheet()
                content.setHtml(
                    f"""
                        {css}
                        <h2>If Statement Example</h2>
                        <p>This is an example of how to use an If statement in your flowchart.</p>
                    """)
        
    def create_faq_tab(self):
        """Create the FAQ tab"""
        print("Creating FAQ tab")
        tab = QWidget()
        layout = QVBoxLayout(tab)
        label = QLabel("This is the FAQ help content.")
        label.setWordWrap(True)
        layout.addWidget(label)
        print("Added label to FAQ tab")
        self.tab_widget.addTab(tab, "FAQ")
    
    def get_content_stylesheet(self):
        """Return CSS stylesheet for QTextEdit content"""
        return """
        <style>
            body {
                background-color: #2B2B2B;
                color: #CCCCCC;
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }
            h3 {
                color: #1F538D;
                font-size: 18px;
                margin-top: 0;
            }
            p {
                color: #CCCCCC;
                margin: 10px 0;
            }
            .highlight {
                color: #2667B3;
                font-weight: bold;
            }
            .code {
                background-color: #1F1F1F;
                color: #90EE90;
                padding: 5px 8px;
                border-radius: 4px;
                font-family: monospace;
            }
            ul {
                color: #CCCCCC;
            }
            li {
                margin: 5px 0;
            }
        </style>
        """
    
    def open(self):
        """Show the window non-blocking"""
        self.show()
        self.raise_()
        self.activateWindow()
        return self