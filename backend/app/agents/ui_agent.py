"""
UI Agent - Visual Consistency and Theme Management
==================================================

Provides skills for generating UI components, themes, and
ensuring visual consistency across the application.
"""

import logging
from typing import Any, Dict, List, Optional
from .base import BaseAgent, AgentContext, Skill

logger = logging.getLogger(__name__)

# Neon Futuristic Theme Configuration
NEON_THEME = {
    "name": "neon-futuristic",
    "colors": {
        "primary": "#00f5ff",  # Cyan neon
        "secondary": "#bf00ff",  # Purple neon
        "accent": "#39ff14",  # Green neon
        "warning": "#ff6b35",  # Orange neon
        "error": "#ff0055",  # Pink neon
        "success": "#00ff88",  # Mint neon
        "background": {
            "dark": "#0a0a1a",
            "medium": "#141428",
            "light": "#1e1e3c",
        },
        "glass": {
            "background": "rgba(20, 20, 40, 0.6)",
            "border": "rgba(0, 245, 255, 0.2)",
            "blur": "20px",
        },
        "gradient": {
            "primary": "linear-gradient(135deg, #00f5ff 0%, #bf00ff 100%)",
            "accent": "linear-gradient(135deg, #39ff14 0%, #00f5ff 100%)",
            "glow": "linear-gradient(135deg, rgba(0, 245, 255, 0.3), rgba(191, 0, 255, 0.3))",
        },
    },
    "effects": {
        "glow": {
            "primary": "0 0 20px rgba(0, 245, 255, 0.5), 0 0 40px rgba(0, 245, 255, 0.3)",
            "secondary": "0 0 20px rgba(191, 0, 255, 0.5), 0 0 40px rgba(191, 0, 255, 0.3)",
            "accent": "0 0 20px rgba(57, 255, 20, 0.5), 0 0 40px rgba(57, 255, 20, 0.3)",
        },
        "glassmorphism": {
            "background": "rgba(20, 20, 40, 0.6)",
            "backdrop_filter": "blur(20px)",
            "border": "1px solid rgba(0, 245, 255, 0.2)",
            "box_shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        },
        "animation": {
            "pulse": "pulse 2s ease-in-out infinite",
            "glow_pulse": "glow-pulse 3s ease-in-out infinite",
            "float": "float 6s ease-in-out infinite",
            "shimmer": "shimmer 2s linear infinite",
        },
    },
    "typography": {
        "font_family": "'Inter', 'Segoe UI', sans-serif",
        "font_family_display": "'Orbitron', 'Space Grotesk', sans-serif",
        "font_weights": {
            "light": 300,
            "regular": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700,
        },
    },
    "spacing": {
        "xs": "4px",
        "sm": "8px",
        "md": "16px",
        "lg": "24px",
        "xl": "32px",
        "xxl": "48px",
    },
    "border_radius": {
        "sm": "8px",
        "md": "12px",
        "lg": "16px",
        "xl": "24px",
        "full": "9999px",
    },
}


class UIAgent(BaseAgent):
    """
    Agent for UI theming and visual consistency.

    Skills:
        - getTheme: Get the current theme configuration
        - generateComponent: Generate UI component styles
        - getAnimationConfig: Get animation configurations
        - generateGradient: Generate custom gradients
    """

    def __init__(self, **kwargs):
        self._current_theme = NEON_THEME
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return "UIAgent"

    @property
    def description(self) -> str:
        return "Manages UI theming, visual consistency, and component styling with neon futuristic aesthetics"

    def _register_skills(self) -> None:
        """Register UI management skills."""

        async def get_theme_handler(
            context: AgentContext,
            section: str = None,
            **kwargs
        ) -> Dict[str, Any]:
            """Get the current theme configuration."""
            if section:
                return {
                    "theme_name": self._current_theme["name"],
                    "section": section,
                    "config": self._current_theme.get(section, {}),
                }
            return self._current_theme

        self.register_skill(Skill(
            name="getTheme",
            description="Get the current neon futuristic theme configuration",
            handler=get_theme_handler,
            output_type="theme_config",
        ))

        async def generate_component_handler(
            context: AgentContext,
            component_type: str = "button",
            variant: str = "primary",
            **kwargs
        ) -> Dict[str, Any]:
            """Generate styles for a UI component."""
            theme = self._current_theme
            colors = theme["colors"]
            effects = theme["effects"]

            base_styles = {
                "button": {
                    "primary": {
                        "background": colors["gradient"]["primary"],
                        "color": "#ffffff",
                        "border": "none",
                        "border_radius": theme["border_radius"]["md"],
                        "padding": f"{theme['spacing']['sm']} {theme['spacing']['lg']}",
                        "font_weight": theme["typography"]["font_weights"]["semibold"],
                        "box_shadow": effects["glow"]["primary"],
                        "transition": "all 0.3s ease",
                        "hover": {
                            "transform": "translateY(-2px)",
                            "box_shadow": f"{effects['glow']['primary']}, 0 10px 30px rgba(0, 245, 255, 0.4)",
                        },
                    },
                    "secondary": {
                        "background": "transparent",
                        "color": colors["primary"],
                        "border": f"2px solid {colors['primary']}",
                        "border_radius": theme["border_radius"]["md"],
                        "padding": f"{theme['spacing']['sm']} {theme['spacing']['lg']}",
                        "font_weight": theme["typography"]["font_weights"]["semibold"],
                        "box_shadow": f"inset 0 0 20px rgba(0, 245, 255, 0.1)",
                        "transition": "all 0.3s ease",
                        "hover": {
                            "background": "rgba(0, 245, 255, 0.1)",
                            "box_shadow": effects["glow"]["primary"],
                        },
                    },
                    "ghost": {
                        "background": "transparent",
                        "color": colors["primary"],
                        "border": "none",
                        "padding": f"{theme['spacing']['sm']} {theme['spacing']['md']}",
                        "transition": "all 0.3s ease",
                        "hover": {
                            "background": "rgba(0, 245, 255, 0.1)",
                            "text_shadow": effects["glow"]["primary"],
                        },
                    },
                },
                "card": {
                    "primary": {
                        **effects["glassmorphism"],
                        "border_radius": theme["border_radius"]["lg"],
                        "padding": theme["spacing"]["lg"],
                        "transition": "all 0.3s ease",
                        "hover": {
                            "border_color": colors["primary"],
                            "box_shadow": f"0 8px 32px rgba(0, 245, 255, 0.2)",
                        },
                    },
                    "elevated": {
                        "background": colors["background"]["medium"],
                        "border": f"1px solid {colors['glass']['border']}",
                        "border_radius": theme["border_radius"]["lg"],
                        "padding": theme["spacing"]["lg"],
                        "box_shadow": "0 20px 60px rgba(0, 0, 0, 0.5)",
                    },
                },
                "input": {
                    "primary": {
                        "background": "rgba(20, 20, 40, 0.8)",
                        "border": f"1px solid rgba(0, 245, 255, 0.3)",
                        "border_radius": theme["border_radius"]["md"],
                        "padding": f"{theme['spacing']['sm']} {theme['spacing']['md']}",
                        "color": "#ffffff",
                        "transition": "all 0.3s ease",
                        "focus": {
                            "border_color": colors["primary"],
                            "box_shadow": f"0 0 10px rgba(0, 245, 255, 0.3)",
                            "outline": "none",
                        },
                    },
                },
                "badge": {
                    "primary": {
                        "background": colors["gradient"]["primary"],
                        "color": "#ffffff",
                        "padding": f"{theme['spacing']['xs']} {theme['spacing']['sm']}",
                        "border_radius": theme["border_radius"]["full"],
                        "font_size": "12px",
                        "font_weight": theme["typography"]["font_weights"]["semibold"],
                    },
                    "glow": {
                        "background": "transparent",
                        "color": colors["primary"],
                        "padding": f"{theme['spacing']['xs']} {theme['spacing']['sm']}",
                        "border": f"1px solid {colors['primary']}",
                        "border_radius": theme["border_radius"]["full"],
                        "font_size": "12px",
                        "box_shadow": effects["glow"]["primary"],
                    },
                },
            }

            component_styles = base_styles.get(component_type, {}).get(variant, {})

            return {
                "component": component_type,
                "variant": variant,
                "styles": component_styles,
            }

        self.register_skill(Skill(
            name="generateComponent",
            description="Generate styles for a UI component with neon aesthetics",
            handler=generate_component_handler,
            output_type="component_styles",
        ))

        async def get_animation_config_handler(
            context: AgentContext,
            animation_type: str = "all",
            **kwargs
        ) -> Dict[str, Any]:
            """Get animation configurations for Framer Motion."""
            animations = {
                "fadeIn": {
                    "initial": {"opacity": 0},
                    "animate": {"opacity": 1},
                    "exit": {"opacity": 0},
                    "transition": {"duration": 0.3},
                },
                "slideUp": {
                    "initial": {"opacity": 0, "y": 20},
                    "animate": {"opacity": 1, "y": 0},
                    "exit": {"opacity": 0, "y": -20},
                    "transition": {"duration": 0.4, "ease": "easeOut"},
                },
                "slideIn": {
                    "initial": {"opacity": 0, "x": -20},
                    "animate": {"opacity": 1, "x": 0},
                    "exit": {"opacity": 0, "x": 20},
                    "transition": {"duration": 0.4, "ease": "easeOut"},
                },
                "scale": {
                    "initial": {"opacity": 0, "scale": 0.9},
                    "animate": {"opacity": 1, "scale": 1},
                    "exit": {"opacity": 0, "scale": 0.9},
                    "transition": {"duration": 0.3, "ease": "easeOut"},
                },
                "glow": {
                    "animate": {
                        "boxShadow": [
                            "0 0 20px rgba(0, 245, 255, 0.3)",
                            "0 0 40px rgba(0, 245, 255, 0.5)",
                            "0 0 20px rgba(0, 245, 255, 0.3)",
                        ],
                    },
                    "transition": {"duration": 2, "repeat": "Infinity", "ease": "easeInOut"},
                },
                "pulse": {
                    "animate": {
                        "scale": [1, 1.05, 1],
                        "opacity": [1, 0.8, 1],
                    },
                    "transition": {"duration": 2, "repeat": "Infinity", "ease": "easeInOut"},
                },
                "float": {
                    "animate": {
                        "y": [0, -10, 0],
                    },
                    "transition": {"duration": 3, "repeat": "Infinity", "ease": "easeInOut"},
                },
                "energyWave": {
                    "animate": {
                        "scale": [1, 1.5, 2],
                        "opacity": [0.6, 0.3, 0],
                    },
                    "transition": {"duration": 2, "repeat": "Infinity", "ease": "easeOut"},
                },
                "neuralPulse": {
                    "animate": {
                        "pathLength": [0, 1],
                        "opacity": [0, 1, 0],
                    },
                    "transition": {"duration": 1.5, "repeat": "Infinity", "ease": "linear"},
                },
                "stagger": {
                    "container": {
                        "animate": {"transition": {"staggerChildren": 0.1}},
                    },
                    "item": {
                        "initial": {"opacity": 0, "y": 20},
                        "animate": {"opacity": 1, "y": 0},
                    },
                },
            }

            if animation_type == "all":
                return {"animations": animations}
            return {"animation": animations.get(animation_type, {})}

        self.register_skill(Skill(
            name="getAnimationConfig",
            description="Get Framer Motion animation configurations",
            handler=get_animation_config_handler,
            output_type="animation_config",
        ))

        async def generate_gradient_handler(
            context: AgentContext,
            colors: List[str] = None,
            angle: int = 135,
            gradient_type: str = "linear",
            **kwargs
        ) -> Dict[str, Any]:
            """Generate custom gradients."""
            if not colors:
                colors = [self._current_theme["colors"]["primary"],
                         self._current_theme["colors"]["secondary"]]

            if gradient_type == "linear":
                gradient = f"linear-gradient({angle}deg, {', '.join(colors)})"
            elif gradient_type == "radial":
                gradient = f"radial-gradient(circle, {', '.join(colors)})"
            elif gradient_type == "conic":
                gradient = f"conic-gradient(from {angle}deg, {', '.join(colors)})"
            else:
                gradient = f"linear-gradient({angle}deg, {', '.join(colors)})"

            return {
                "gradient": gradient,
                "colors": colors,
                "type": gradient_type,
                "angle": angle,
            }

        self.register_skill(Skill(
            name="generateGradient",
            description="Generate custom neon gradients",
            handler=generate_gradient_handler,
            output_type="gradient",
        ))

        async def get_chatbot_visualization_handler(
            context: AgentContext,
            state: str = "idle",  # idle, active, thinking, success, error
            **kwargs
        ) -> Dict[str, Any]:
            """Get chatbot visualization configuration with neon effects."""
            theme = self._current_theme

            visualizations = {
                "idle": {
                    "ring": {
                        "color": theme["colors"]["primary"],
                        "animation": "pulse",
                        "glow": theme["effects"]["glow"]["primary"],
                    },
                    "background": {
                        "gradient": theme["colors"]["gradient"]["glow"],
                        "animation": "none",
                    },
                },
                "active": {
                    "ring": {
                        "color": theme["colors"]["primary"],
                        "animation": "glow-pulse",
                        "glow": f"0 0 30px rgba(0, 245, 255, 0.6), 0 0 60px rgba(0, 245, 255, 0.4)",
                    },
                    "energyWaves": {
                        "enabled": True,
                        "color": "rgba(0, 245, 255, 0.3)",
                        "count": 3,
                        "animation": "energyWave",
                    },
                    "neuralNetwork": {
                        "enabled": True,
                        "color": theme["colors"]["primary"],
                        "nodeCount": 6,
                        "animation": "neuralPulse",
                    },
                },
                "thinking": {
                    "ring": {
                        "color": theme["colors"]["secondary"],
                        "animation": "spin",
                        "glow": theme["effects"]["glow"]["secondary"],
                    },
                    "energyWaves": {
                        "enabled": True,
                        "color": "rgba(191, 0, 255, 0.3)",
                        "count": 5,
                        "animation": "energyWave",
                    },
                    "particles": {
                        "enabled": True,
                        "color": theme["colors"]["secondary"],
                        "count": 20,
                    },
                },
                "success": {
                    "ring": {
                        "color": theme["colors"]["success"],
                        "animation": "pulse",
                        "glow": theme["effects"]["glow"]["accent"],
                    },
                    "burst": {
                        "enabled": True,
                        "color": theme["colors"]["success"],
                    },
                },
                "error": {
                    "ring": {
                        "color": theme["colors"]["error"],
                        "animation": "shake",
                        "glow": "0 0 20px rgba(255, 0, 85, 0.5)",
                    },
                },
            }

            return {
                "state": state,
                "visualization": visualizations.get(state, visualizations["idle"]),
                "cssVariables": {
                    "--chatbot-neon-primary": theme["colors"]["primary"],
                    "--chatbot-neon-secondary": theme["colors"]["secondary"],
                    "--chatbot-neon-glow": theme["effects"]["glow"]["primary"],
                    "--chatbot-glass-bg": theme["effects"]["glassmorphism"]["background"],
                    "--chatbot-glass-blur": theme["effects"]["glassmorphism"]["backdrop_filter"],
                },
            }

        self.register_skill(Skill(
            name="getChatbotVisualization",
            description="Get chatbot visualization config with neon effects",
            handler=get_chatbot_visualization_handler,
            output_type="visualization_config",
        ))
