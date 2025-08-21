"""
Gradio web interface for the Sidekick AI application.
Provides a clean, modern UI for interacting with the AI assistant.
"""

import gradio as gr
from typing import List, Dict, Any, Optional
import asyncio
import logging

from src.core.sidekick import Sidekick
from src.utils.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SidekickUI:
    """
    Gradio UI wrapper for the Sidekick AI application.
    
    Handles UI state management, async operations, and resource cleanup.
    """
    
    def __init__(self):
        """Initialize the UI wrapper."""
        self.sidekick: Optional[Sidekick] = None
        self._is_initialized = False
    
    async def setup(self) -> Sidekick:
        """
        Set up the Sidekick instance.
        
        Returns:
            Initialized Sidekick instance
            
        Raises:
            Exception: If setup fails
        """
        try:
            if not self._is_initialized:
                logger.info("Initializing Sidekick...")
                self.sidekick = Sidekick()
                await self.sidekick.setup()
                self._is_initialized = True
                logger.info("Sidekick initialized successfully")
            
            return self.sidekick
            
        except Exception as e:
            logger.error(f"Failed to initialize Sidekick: {e}")
            self._is_initialized = False
            raise
    
    async def process_message(
        self, 
        sidekick: Sidekick, 
        message: str, 
        success_criteria: str, 
        history: List[Dict[str, str]]
    ) -> tuple[List[Dict[str, str]], Sidekick]:
        """
        Process a user message through the Sidekick workflow.
        
        Args:
            sidekick: Sidekick instance
            message: User message
            success_criteria: Success criteria for the task
            history: Conversation history
            
        Returns:
            Tuple of updated history and sidekick instance
        """
        try:
            if not message.strip():
                return history, sidekick
            
            logger.info(f"Processing message: {message[:100]}...")
            
            # Run the workflow
            results = await sidekick.run_superstep(message, success_criteria, history)
            
            logger.info("Message processed successfully")
            return results, sidekick
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_message = {
                "role": "assistant", 
                "content": f"Sorry, I encountered an error: {str(e)}"
            }
            return history + [error_message], sidekick
    
    async def reset(self) -> tuple[str, str, List[Dict[str, str]], Sidekick]:
        """
        Reset the conversation and create a new Sidekick instance.
        
        Returns:
            Tuple of reset values and new sidekick instance
        """
        try:
            logger.info("Resetting conversation...")
            
            # Clean up old instance
            if self.sidekick and self._is_initialized:
                await self.sidekick.cleanup()
            
            # Create new instance
            new_sidekick = Sidekick()
            await new_sidekick.setup()
            
            self.sidekick = new_sidekick
            self._is_initialized = True
            
            logger.info("Conversation reset successfully")
            return "", "", [], new_sidekick
            
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}")
            # Return current state if reset fails
            return "", "", [], self.sidekick or Sidekick()
    
    def free_resources(self, sidekick: Sidekick) -> None:
        """
        Clean up resources when the UI is closed.
        
        Args:
            sidekick: Sidekick instance to clean up
        """
        try:
            logger.info("Cleaning up resources...")
            if sidekick and self._is_initialized:
                asyncio.create_task(sidekick.cleanup())
                self._is_initialized = False
            logger.info("Resources cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Exception during cleanup: {e}")
    
    def create_ui(self) -> gr.Blocks:
        """
        Create the Gradio UI interface.
        
        Returns:
            Configured Gradio Blocks interface
        """
        with gr.Blocks(
            title="Sidekick AI - Personal Co-Worker", 
            theme=gr.themes.Default(primary_hue="emerald")
        ) as ui:
            
            # Header
            gr.Markdown("## 🤖 Sidekick AI - Your Personal Co-Worker")
            gr.Markdown("""
            **How it works:**
            1. Describe your task in the message field
            2. Define your success criteria
            3. Click "Go!" and watch Sidekick work until completion
            4. Use "Reset" to start a new conversation
            """)
            
            # State management
            sidekick = gr.State(delete_callback=self.free_resources)
            
            # Chat interface
            with gr.Row():
                chatbot = gr.Chatbot(
                    label="Conversation", 
                    height=400, 
                    type="messages",
                    show_label=True
                )
            
            # Input controls
            with gr.Group():
                with gr.Row():
                    message = gr.Textbox(
                        show_label=False, 
                        placeholder="What would you like me to help you with?",
                        lines=2
                    )
                
                with gr.Row():
                    success_criteria = gr.Textbox(
                        show_label=False, 
                        placeholder="What defines success for this task? (optional)",
                        lines=2
                    )
                
                with gr.Row():
                    reset_button = gr.Button("🔄 Reset", variant="stop", size="sm")
                    go_button = gr.Button("🚀 Go!", variant="primary", size="lg")
            
            # Status and info
            with gr.Accordion("ℹ️ About Sidekick", open=False):
                gr.Markdown("""
                **Capabilities:**
                - 🌐 Web browsing and research
                - 📁 File creation and management
                - 🐍 Python code execution
                - 🔍 Web search and Wikipedia lookup
                - 📱 Push notifications
                
                **Features:**
                - Self-evaluating workflow
                - Iterative improvement
                - Context-aware conversations
                - Resource management
                """)
            
            # Event handlers
            ui.load(self.setup, [], [sidekick])
            
            # Message submission
            message.submit(
                self.process_message, 
                [sidekick, message, success_criteria, chatbot], 
                [chatbot, sidekick]
            )
            
            # Success criteria submission
            success_criteria.submit(
                self.process_message, 
                [sidekick, message, success_criteria, chatbot], 
                [chatbot, sidekick]
            )
            
            # Go button
            go_button.click(
                self.process_message, 
                [sidekick, message, success_criteria, chatbot], 
                [chatbot, sidekick]
            )
            
            # Reset button
            reset_button.click(
                self.reset, 
                [], 
                [message, success_criteria, chatbot, sidekick]
            )
        
        return ui


def create_app() -> gr.Blocks:
    """
    Create and configure the Gradio application.
    
    Returns:
        Configured Gradio Blocks interface
    """
    ui_wrapper = SidekickUI()
    return ui_wrapper.create_ui()


def launch_app(
    host: str = None,
    port: int = None,
    share: bool = False,
    inbrowser: bool = True
) -> None:
    """
    Launch the Gradio application.
    
    Args:
        host: Host address to bind to
        port: Port to bind to
        share: Whether to create a public link
        inbrowser: Whether to open in browser
    """
    host = host or config.APP_HOST
    port = port or config.APP_PORT
    
    app = create_app()
    
    logger.info(f"Starting Sidekick AI on {host}:{port}")
    
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        inbrowser=inbrowser,
        show_error=True
    )


if __name__ == "__main__":
    launch_app()
