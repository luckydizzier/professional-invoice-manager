"""
Style manager for loading and applying CSS styles
"""

from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import QApplication


class StyleManager:
    """Manages application styles and themes"""
    
    def __init__(self, styles_dir: str = "styles"):
        self.styles_dir = Path(styles_dir)
        self.current_theme = "default"
        self._loaded_styles = {}
    
    def load_style_file(self, filename: str) -> str:
        """Load CSS content from file"""
        if filename in self._loaded_styles:
            return self._loaded_styles[filename]
        
        style_path = self.styles_dir / filename
        if style_path.exists():
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._loaded_styles[filename] = content
                    return content
            except IOError as e:
                print(f"Warning: Could not load style file {filename}: {e}")
        else:
            print(f"Warning: Style file {filename} not found")
        
        return ""
    
    def get_main_styles(self) -> str:
        """Get main application styles"""
        return self.load_style_file("main.css")
    
    def get_dialog_styles(self) -> str:
        """Get dialog styles"""
        return self.load_style_file("dialogs.css")
    
    def get_combined_styles(self) -> str:
        """Get all styles combined"""
        main_styles = self.get_main_styles()
        dialog_styles = self.get_dialog_styles()
        return f"{main_styles}\n\n{dialog_styles}"
    
    def apply_styles(self, app: QApplication) -> None:
        """Apply styles to the application"""
        combined_styles = self.get_combined_styles()
        if combined_styles:
            app.setStyleSheet(combined_styles)
    
    def clear_cache(self) -> None:
        """Clear the style cache"""
        self._loaded_styles.clear()
    
    def reload_styles(self, app: Optional[QApplication] = None) -> None:
        """Reload styles from files"""
        self.clear_cache()
        if app:
            self.apply_styles(app)


# Global style manager instance
style_manager = StyleManager()
