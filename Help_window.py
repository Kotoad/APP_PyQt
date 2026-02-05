from Imports import (QDialog, Qt, QVBoxLayout, QLabel, QTabWidget, QWidget, QFont, QTextEdit,
                     QScrollArea, QPushButton,Path, os, get_utils)

Utils = get_utils()

class HelpWindow(QDialog):
    """Singleton Help Window"""
    _instance = None

    def __init__(self, parent=None, which=0):
        super().__init__(parent)
        self.parent_canvas = parent
        self.which = which
        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        self.base_path = Utils.get_base_path()
        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent, which):
        """Get or create singleton instance"""
        if cls._instance is not None:
            try:
                if cls._instance.isVisible():
                    return cls._instance
            except RuntimeError:
                cls._instance = None
        
        if cls._instance is None:
            cls._instance = cls(parent, which)
        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(self.t("help_window.window_title"))
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
        #print("Creating Getting Started tab")
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)
        
        css = self.get_content_stylesheet()

        html_file_path = self.t("help_window.getting_started_tab.content")

        base_dir = self.base_path
        full_path = base_dir / html_file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                html_template = f.read()

                html_content = html_template.format(css=css)
            
            # Now use html_content in your QTextEdit or wherever you need it
            # For example:
            # self.help_text_widget.setHtml(html_content)
            
        except FileNotFoundError:
            print(f"Help file not found: {full_path}")
            html_content = self.t("help_window.getting_started_tab.file_not_found")
        except Exception as e:
            print(f"Error loading help content: {e}")
            html_content = self.t("help_window.getting_started_tab.error_loading_file")

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(html_content)
        
        layout.addWidget(text_edit)
        #print("Added label to Getting Started tab")
        self.tab_widget.addTab(tab, self.t("help_window.getting_started_tab.title"))

    def create_examples_tab(self):
        """Create the Examples tab with scrollable vertical examples"""
        #print("Creating Examples tab")
        self.examples_tab = QWidget()
        self.examples_layout = QVBoxLayout(self.examples_tab)
        self.examples_layout.setContentsMargins(0, 0, 0, 0)
        
        self.show_examples_list()
        
        self.tab_widget.addTab(self.examples_tab, self.t("help_window.examples_tab.title"))
        #print("Added scrollable examples to Examples tab")

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
            (self.t("help_window.examples_tab.examples.example_1.title"), self.t("help_window.examples_tab.examples.example_1.description"), "1"),
            (self.t("help_window.examples_tab.examples.example_2.title"), self.t("help_window.examples_tab.examples.example_2.description"), "2"),
            (self.t("help_window.examples_tab.examples.example_3.title"), self.t("help_window.examples_tab.examples.example_3.description"), "3"),
            (self.t("help_window.examples_tab.examples.example_4.title"), self.t("help_window.examples_tab.examples.example_4.description"), "4"),
            (self.t("help_window.examples_tab.examples.example_5.title"), self.t("help_window.examples_tab.examples.example_5.description"), "5"),
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
        
        view_btn = QPushButton(self.t("help_window.examples_tab.show_example_button"))
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
        back_btn = QPushButton(self.t("help_window.examples_tab.back_to_examples_button"))
        back_btn.setMaximumWidth(150)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.show_examples_list)
        detail_layout.addWidget(back_btn)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1F538D;")
        detail_layout.addWidget(title_label)
        
        content = QTextEdit()
        content.setReadOnly(True)
        self.fill_content_area(content, example_id)
        detail_layout.addWidget(content)
        
        # Add to tab
        self.examples_layout.addWidget(detail_widget)

    def fill_content_area(self, content, example_id):
        css = self.get_content_stylesheet()
        #print(f"Filling content area for example ID: {example_id}")
        match example_id:
            case "1":
                #print("Filling content for Example 1")
                current_dir = self.base_path
                Blinking_LED_Diagram = os.path.join(current_dir, "resources", "images", "Blinking_LED", "blinking_led_diagram.png")
                Blinking_LED_Diagram = os.path.abspath(Blinking_LED_Diagram)  # Convert to absolute path
                Blinking_LED_Diagram = Blinking_LED_Diagram.replace("\\", "/")
                Blinking_LED_Flowchart = os.path.join(current_dir, "resources", "images", "Blinking_LED", "blinking_led_flowchart.png")
                Blinking_LED_Flowchart = os.path.abspath(Blinking_LED_Flowchart)
                Blinking_LED_Flowchart = Blinking_LED_Flowchart.replace("\\", "/")

                html_file_path = self.t("help_window.examples_tab.examples.example_1.content")
 
                full_path = current_dir / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()
                        html_content = html_template.format(
                            css=css,
                            Blinking_LED_Diagram=Blinking_LED_Diagram,
                            Blinking_LED_Flowchart=Blinking_LED_Flowchart
                        )
                    # Now use html_content in your QTextEdit or wherever you need it
                    # For example:
                    # self.help_text_widget.setHtml(html_content)
                    
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.examples_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.examples_tab.error_loading_file")
                #print(f"Image path for help content: {Blinking_LED_Diagram}")

                content.setHtml(html_content)
            case "2":
                html_file_path = self.t("help_window.examples_tab.examples.example_2.content")

                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)

                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.examples_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.examples_tab.error_loading_file")

                    #print("Filling content for Example 2")
                content.setHtml(html_content)
            case "3":
                html_file_path = self.t("help_window.examples_tab.examples.example_3.content")
                
                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.examples_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.examples_tab.error_loading_file")
                #print("Filling content for Example 3")
                content.setHtml(html_content)
            case "4":
                html_file_path = self.t("help_window.examples_tab.examples.example_4.content")

                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.examples_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.examples_tab.error_loading_file")
    
                #print("Filling content for Example 4")
                content.setHtml(html_content)
            case "5":
                html_file_path = self.t("help_window.examples_tab.examples.example_5.content")

                full_path = self.base_path / html_file_path

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        html_template = f.read()

                        html_content = html_template.format(css=css)
                except FileNotFoundError:
                    print(f"Help file not found: {full_path}")
                    html_content = self.t("help_window.examples_tab.file_not_found")
                except Exception as e:
                    print(f"Error loading help content: {e}")
                    html_content = self.t("help_window.examples_tab.error_loading_file")

                #print("Filling content for Example 5")
                content.setHtml(html_content)
        
    def create_faq_tab(self):
        """Create the FAQ tab"""
        #print("Creating FAQ tab")
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        css = self.get_content_stylesheet()

        html_file_path = self.t("help_window.faq_tab.content")
        full_path = self.base_path / html_file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                html_template = f.read()

                html_content = html_template.format(css=css)
        except FileNotFoundError:
            print(f"Help file not found: {full_path}")
            html_content = self.t("help_window.faq_tab.file_not_found")
        except Exception as e:
            print(f"Error loading FAQ content: {e}")
            html_content = self.t("help_window.faq_tab.error_loading_file")
        
        text_edit.setHtml(html_content)
        layout.addWidget(text_edit)
        #print("Added label to FAQ tab")
        self.tab_widget.addTab(tab, self.t("help_window.faq_tab.title"))
    
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

    def closeEvent(self, event):
        """Handle close event"""
        #print("HelpWindow closeEvent called")
        self.state_manager.app_state.on_help_dialog_close()
        event.accept()