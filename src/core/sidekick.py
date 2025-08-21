"""
Core Sidekick AI class implementing the LangGraph workflow.
Handles task processing, evaluation, and tool management.
"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.core.state import State, EvaluatorOutput, create_initial_state
from src.tools.browser import playwright_tools, cleanup_browser
from src.tools.external import other_tools
from src.utils.config import config


class Sidekick:
    """
    Main Sidekick AI class that manages the LangGraph workflow.
    
    This class orchestrates the entire AI workflow including:
    - Tool initialization and management
    - LangGraph workflow execution
    - State management and evaluation
    - Resource cleanup
    """
    
    def __init__(self):
        """Initialize the Sidekick instance."""
        self.worker_llm_with_tools = None
        self.evaluator_llm_with_output = None
        self.tools = None
        self.graph = None
        self.sidekick_id = str(uuid.uuid4())
        self.memory = MemorySaver()
        self.browser = None
        self.playwright = None
        self._is_initialized = False
    
    async def setup(self) -> None:
        """
        Set up the Sidekick instance with all required components.
        
        Raises:
            RuntimeError: If setup fails
        """
        try:
            # Validate configuration
            config.validate()
            
            # Initialize tools
            self.tools, self.browser, self.playwright = await playwright_tools()
            self.tools += await other_tools()
            
            # Initialize LLMs
            worker_llm = ChatOpenAI(model="gpt-4o-mini")
            self.worker_llm_with_tools = worker_llm.bind_tools(self.tools)
            
            evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
            self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
            
            # Build the workflow graph
            await self.build_graph()
            
            self._is_initialized = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to setup Sidekick: {e}")
    
    def _create_system_message(self, state: State) -> str:
        """
        Create the system message for the worker LLM.
        
        Args:
            state: Current workflow state
            
        Returns:
            Formatted system message
        """
        system_message = f"""You are a helpful assistant that can use tools to complete tasks.
You keep working on a task until either you have a question or clarification for the user, or the success criteria is met.
You have many tools to help you, including tools to browse the internet, navigating and retrieving web pages.
You have a tool to run python code, but note that you would need to include a print() statement if you wanted to receive output.
The current date and time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This is the success criteria:
{state["success_criteria"]}
You should reply either with a question for the user about this assignment, or with your final response.
If you have a question for the user, you need to reply by clearly stating your question. An example might be:

Question: please clarify whether you want a summary or a detailed answer

If you've finished, reply with the final answer, and don't ask a question; simply reply with the answer.
"""

        if state.get("feedback_on_work"):
            system_message += f"""

Previously you thought you completed the assignment, but your reply was rejected because the success criteria was not met.
Here is the feedback on why this was rejected:
{state["feedback_on_work"]}
With this feedback, please continue the assignment, ensuring that you meet the success criteria or have a question for the user."""

        return system_message
    
    def worker(self, state: State) -> Dict[str, Any]:
        """
        Worker node that processes user requests using available tools.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with worker response
        """
        system_message = self._create_system_message(state)
        
        # Update or add system message
        messages = state["messages"]
        found_system_message = False
        
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True
                break
        
        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages
        
        # Invoke the LLM with tools
        response = self.worker_llm_with_tools.invoke(messages)
        
        return {"messages": [response]}
    
    def worker_router(self, state: State) -> str:
        """
        Route worker output to either tools or evaluator.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node to execute
        """
        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "evaluator"
    
    def _format_conversation(self, messages: List[Any]) -> str:
        """
        Format conversation history for evaluation.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Formatted conversation string
        """
        conversation = "Conversation history:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Tools use]"
                conversation += f"Assistant: {text}\n"
        return conversation
    
    def evaluator(self, state: State) -> State:
        """
        Evaluate whether the task has been completed successfully.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with evaluation results
        """
        last_response = state["messages"][-1].content
        
        system_message = """You are an evaluator that determines if a task has been completed successfully by an Assistant.
Assess the Assistant's last response based on the given criteria. Respond with your feedback, and with your decision on whether the success criteria has been met,
and whether more input is needed from the user."""

        user_message = f"""You are evaluating a conversation between the User and Assistant. You decide what action to take based on the last response from the Assistant.

The entire conversation with the assistant, with the user's original request and all replies, is:
{self._format_conversation(state["messages"])}

The success criteria for this assignment is:
{state["success_criteria"]}

And the final response from the Assistant that you are evaluating is:
{last_response}

Respond with your feedback, and decide if the success criteria is met by this response.
Also, decide if more user input is required, either because the assistant has a question, needs clarification, or seems to be stuck and unable to answer without help.

The Assistant has access to a tool to write files. If the Assistant says they have written a file, then you can assume they have done so.
Overall you should give the Assistant the benefit of the doubt if they say they've done something. But you should reject if you feel that more work should go into this.
"""

        if state["feedback_on_work"]:
            user_message += f"""Also, note that in a prior attempt from the Assistant, you provided this feedback: {state['feedback_on_work']}
If you're seeing the Assistant repeating the same mistakes, then consider responding that user input is required."""

        evaluator_messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message),
        ]

        eval_result = self.evaluator_llm_with_output.invoke(evaluator_messages)
        
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": f"Evaluator Feedback on this answer: {eval_result.feedback}",
                }
            ],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": eval_result.success_criteria_met,
            "user_input_needed": eval_result.user_input_needed,
        }
    
    def route_based_on_evaluation(self, state: State) -> str:
        """
        Route based on evaluation results.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node to execute
        """
        if state["success_criteria_met"] or state["user_input_needed"]:
            return "END"
        else:
            return "worker"
    
    async def build_graph(self) -> None:
        """
        Build the LangGraph workflow.
        
        Raises:
            RuntimeError: If graph building fails
        """
        try:
            # Set up Graph Builder with State
            graph_builder = StateGraph(State)

            # Add nodes
            graph_builder.add_node("worker", self.worker)
            graph_builder.add_node("tools", ToolNode(tools=self.tools))
            graph_builder.add_node("evaluator", self.evaluator)

            # Add edges
            graph_builder.add_conditional_edges(
                "worker", self.worker_router, {"tools": "tools", "evaluator": "evaluator"}
            )
            graph_builder.add_edge("tools", "worker")
            graph_builder.add_conditional_edges(
                "evaluator", self.route_based_on_evaluation, {"worker": "worker", "END": END}
            )
            graph_builder.add_edge(START, "worker")

            # Compile the graph
            self.graph = graph_builder.compile(checkpointer=self.memory)
            
        except Exception as e:
            raise RuntimeError(f"Failed to build graph: {e}")
    
    async def run_superstep(self, message: str, success_criteria: str, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Run a single superstep of the workflow.
        
        Args:
            message: User message
            success_criteria: Success criteria for the task
            history: Conversation history
            
        Returns:
            Updated conversation history
            
        Raises:
            RuntimeError: If Sidekick is not initialized or execution fails
        """
        if not self._is_initialized:
            raise RuntimeError("Sidekick not initialized. Call setup() first.")
        
        try:
            config = {"configurable": {"thread_id": self.sidekick_id}}
            
            # Create initial state
            state = create_initial_state(message, success_criteria)
            
            # Run the workflow
            result = await self.graph.ainvoke(state, config=config)
            
            # Format results
            user = {"role": "user", "content": message}
            reply = {"role": "assistant", "content": result["messages"][-2].content}
            feedback = {"role": "assistant", "content": result["messages"][-1].content}
            
            return history + [user, reply, feedback]
            
        except Exception as e:
            raise RuntimeError(f"Failed to run superstep: {e}")
    
    async def cleanup(self) -> None:
        """
        Clean up resources and perform graceful shutdown.
        """
        try:
            if self.browser and self.playwright:
                await cleanup_browser(self.browser, self.playwright)
                self.browser = None
                self.playwright = None
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
        finally:
            self._is_initialized = False
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        if hasattr(self, '_is_initialized') and self._is_initialized:
            try:
                # Try to run cleanup in a new event loop if none exists
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.cleanup())
                else:
                    asyncio.run(self.cleanup())
            except Exception:
                # If cleanup fails, just log it
                pass
