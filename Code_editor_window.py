from Imports import (QDialog, pyqtSignal, QObject, QsciLexerPython, QFont,
                      QsciScintilla, QsciAPIs, Qt, QColor, QVBoxLayout) 
import keyword, builtins

from Imports import get_utils
Utils = get_utils()

class CodeEditorWindow(QDialog):
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            try:
                _ = cls._instance.isVisible()  # Check if the instance is still valid
                if cls._instance.is_hidden:
                    cls._instance = None  # Reset instance if it was hidden
            except RuntimeError:
                cls._instance = None  # Reset instance if it was deleted
            except Exception as e:
                cls._instance = None  # Reset instance on any unexpected error
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self, parent=None):
        super().__init__()
        self.parent_canvas = parent
        self.is_hidden = True

        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle(self.t("code_editor_window.window_title"))
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.WindowType.Window)
        
        self.editor = QsciScintilla(self)
        
        # 1. FIX: Make Lexer an instance variable and give it a parent
        self.lexer = QsciLexerPython(self.editor) 
        
        self.set_theme(self.lexer, self.editor)

        self.editor.setLexer(self.lexer)

        self.editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        self.editor.setIndentationGuides(True)
        self.editor.setIndentationsUseTabs(False)
        self.editor.setTabWidth(4)

        # 2. FIX: Make API an instance variable and attach it to self.lexer
        self.api = QsciAPIs(self.lexer)

        for kw in keyword.kwlist:
            self.api.add(kw)
        for builtin in dir(builtins):
            if not builtin.startswith("__"):
                self.api.add(builtin + "()")  # Add parentheses to indicate callable
        
        self.api.prepare()

        self.editor.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.editor.setAutoCompletionThreshold(2)
        self.editor.setAutoCompletionCaseSensitivity(False)
        self.editor.setAutoCompletionReplaceWord(False)
        self.editor.setAutoCompletionShowSingle(True)
        self.editor.setAutoCompletionFillupsEnabled(True)

        with open("File.py", "r", encoding="utf-8") as f:
            sample_code = f.read()
            self.editor.setText(sample_code)

        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def set_theme(self, lexer, editor):
        material_font = QFont("Monospace", 11)
        lexer.setDefaultFont(material_font)
        lexer.setFont(material_font)

        # --- 2. Base Editor Colors ---
        bg_color = QColor("#212121")          # Material Darker Background
        fg_color = QColor("#EEFFFF")          # Material Default Text
        selection_bg = QColor("#2C3941")      # Highlighted text background
        caret_color = QColor("#FFCC00")       # Yellow cursor
        current_line_bg = QColor("#2F2F2F")   # Active line highlight
        margin_fg = QColor("#4A4A4A")         # Line numbers color

        # Apply base colors to the Lexer
        lexer.setDefaultPaper(bg_color)
        lexer.setDefaultColor(fg_color)
        lexer.setPaper(bg_color)
        lexer.setColor(fg_color)

        # Apply base colors to the Editor
        editor.setPaper(bg_color)
        editor.setCaretForegroundColor(caret_color)
        editor.setCaretWidth(2)
        editor.setSelectionBackgroundColor(selection_bg)

        editor.setMarginLineNumbers(0, True)  # Turns on line numbers for margin 0
        editor.setMarginWidth(0, "00000")  # Adjust margin width based on expected line count

        editor.setFoldMarginColors(bg_color, bg_color)

        # Highlight the line the cursor is currently on
        editor.setCaretLineVisible(True)
        editor.setCaretLineBackgroundColor(current_line_bg)

        # Line Numbers (Margins)
        editor.setMarginsBackgroundColor(bg_color)
        editor.setMarginsForegroundColor(margin_fg)

        # --- 3. Material Darker Syntax Highlighting ---
        
        # Keywords (def, class, if, return...) -> Purple
        lexer.setColor(QColor("#C792EA"), QsciLexerPython.Keyword)
        
        # Classes -> Yellow/Orange
        lexer.setColor(QColor("#FFCB6B"), QsciLexerPython.ClassName)
        
        # Function & Method Names (when defining them) -> Blue
        lexer.setColor(QColor("#82AAFF"), QsciLexerPython.FunctionMethodName)
        
        # Strings -> Light Green
        string_color = QColor("#C3E88D")
        lexer.setColor(string_color, QsciLexerPython.SingleQuotedString)
        lexer.setColor(string_color, QsciLexerPython.DoubleQuotedString)
        lexer.setColor(string_color, QsciLexerPython.TripleSingleQuotedString)
        lexer.setColor(string_color, QsciLexerPython.TripleDoubleQuotedString)
        
        # Numbers -> Orange
        lexer.setColor(QColor("#F78C6C"), QsciLexerPython.Number)
        
        # Comments -> Faded Blue/Grey (You can also make them italic!)
        comment_color = QColor("#546E7A")
        lexer.setColor(comment_color, QsciLexerPython.Comment)
        lexer.setColor(comment_color, QsciLexerPython.CommentBlock)
        # Make comments italic
        italic_font = QFont("Monospace", 11)
        italic_font.setItalic(True)
        lexer.setFont(italic_font, QsciLexerPython.Comment)
        lexer.setFont(italic_font, QsciLexerPython.CommentBlock)

        # Decorators (@property, etc) -> Cyan
        lexer.setColor(QColor("#89DDFF"), QsciLexerPython.Decorator)
        
        # Operators (+, -, =, (, ), etc.) -> Cyan
        lexer.setColor(QColor("#89DDFF"), QsciLexerPython.Operator)

        # Standard identifiers and default text -> Off-White
        lexer.setColor(fg_color, QsciLexerPython.Identifier)
        lexer.setColor(fg_color, QsciLexerPython.Default)

    def open(self):
        if self.is_hidden:
            self.is_hidden = False
            with open("File.py", "r", encoding="utf-8") as f:
                sample_code = f.read()
            if self.editor:
                self.editor.setText(sample_code)
            self.show()
            self.raise_()
            self.activateWindow()
        return self
    
    def reject(self):
        self.close()

    def closeEvent(self, event):
        self.is_hidden = True
        self.state_manager.app_state.on_code_editor_dialog_close()
        event.accept()