from collections.abc import Iterable

from mcp.types import Prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.styles import Style

from core.cli_chat import CliChat


class CommandAutoSuggest(AutoSuggest):
    def __init__(self, prompts: list[Prompt]) -> None:
        self.prompt_dict = {prompt.name: prompt for prompt in prompts}

    def get_suggestion(self, buffer: Buffer, document: Document) -> Suggestion | None:
        text = document.text

        if not text.startswith("/"):
            return None

        parts = text[1:].split()

        if len(parts) == 1:
            prompt = self.prompt_dict.get(parts[0])
            if prompt and prompt.arguments:
                return Suggestion(f" {prompt.arguments[0].name}")

        return None


class UnifiedCompleter(Completer):
    def __init__(self) -> None:
        self.prompts: list[Prompt] = []
        self.prompt_dict: dict[str, Prompt] = {}
        self.resources: list[str] = []

    def update_prompts(self, prompts: list[Prompt]) -> None:
        self.prompts = prompts
        self.prompt_dict = {prompt.name: prompt for prompt in prompts}

    def update_resources(self, resources: list[str]) -> None:
        self.resources = resources

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        text = document.text
        text_before_cursor = document.text_before_cursor

        if "@" in text_before_cursor:
            last_at_pos = text_before_cursor.rfind("@")
            prefix = text_before_cursor[last_at_pos + 1 :]

            for resource_id in self.resources:
                if resource_id.lower().startswith(prefix.lower()):
                    yield Completion(
                        resource_id,
                        start_position=-len(prefix),
                        display=resource_id,
                        display_meta="Resource",
                    )
            return

        if text.startswith("/"):
            parts = text[1:].split()

            if len(parts) <= 1 and not text.endswith(" "):
                cmd_prefix = parts[0] if parts else ""

                for prompt in self.prompts:
                    if prompt.name.startswith(cmd_prefix):
                        yield Completion(
                            prompt.name,
                            start_position=-len(cmd_prefix),
                            display=f"/{prompt.name}",
                            display_meta=prompt.description or "",
                        )
                return

            if len(parts) == 1 and text.endswith(" "):
                cmd = parts[0]

                if cmd in self.prompt_dict:
                    for doc_id in self.resources:
                        yield Completion(doc_id, start_position=0, display=doc_id)
                return

            if len(parts) >= 2:
                doc_prefix = parts[-1]

                for doc_id in self.resources:
                    if doc_id.lower().startswith(doc_prefix.lower()):
                        yield Completion(
                            doc_id, start_position=-len(doc_prefix), display=doc_id
                        )
                return


class CliApp:
    def __init__(self, agent: CliChat) -> None:
        self.agent = agent
        self.resources: list[str] = []
        self.prompts: list[Prompt] = []

        self.completer = UnifiedCompleter()
        self.command_autosuggester = CommandAutoSuggest([])

        self.kb = KeyBindings()

        @self.kb.add("/")
        def _(event: KeyPressEvent) -> None:
            buffer = event.app.current_buffer
            buffer.insert_text("/")
            if buffer.document.is_cursor_at_the_end and buffer.text == "/":
                buffer.start_completion(select_first=False)

        @self.kb.add("@")
        def _(event: KeyPressEvent) -> None:
            buffer = event.app.current_buffer
            buffer.insert_text("@")
            if buffer.document.is_cursor_at_the_end:
                buffer.start_completion(select_first=False)

        @self.kb.add(" ")
        def _(event: KeyPressEvent) -> None:
            buffer = event.app.current_buffer
            text = buffer.text

            buffer.insert_text(" ")

            if text.startswith("/"):
                parts = text[1:].split()

                if len(parts) == 1:
                    buffer.start_completion(select_first=False)
                elif len(parts) == 2:
                    arg = parts[1]
                    if (
                        "doc" in arg.lower()
                        or "file" in arg.lower()
                        or "id" in arg.lower()
                    ):
                        buffer.start_completion(select_first=False)

        self.history: InMemoryHistory = InMemoryHistory()
        self.session: PromptSession[str] = PromptSession(
            completer=self.completer,
            history=self.history,
            key_bindings=self.kb,
            style=Style.from_dict(
                {
                    "prompt": "#aaaaaa",
                    "completion-menu.completion": "bg:#222222 #ffffff",
                    "completion-menu.completion.current": "bg:#444444 #ffffff",
                }
            ),
            complete_while_typing=True,
            complete_in_thread=True,
            auto_suggest=self.command_autosuggester,
        )

    async def initialize(self) -> None:
        await self.refresh_resources()
        await self.refresh_prompts()

    async def refresh_resources(self) -> None:
        try:
            self.resources = await self.agent.list_docs_ids()
            self.completer.update_resources(self.resources)
        except Exception as e:  # noqa: BLE001
            print(f"Error refreshing resources: {e}")

    async def refresh_prompts(self) -> None:
        try:
            self.prompts = await self.agent.list_prompts()
            self.completer.update_prompts(self.prompts)
            self.command_autosuggester = CommandAutoSuggest(self.prompts)
            self.session.auto_suggest = self.command_autosuggester
        except Exception as e:  # noqa: BLE001
            print(f"Error refreshing prompts: {e}")

    async def run(self) -> None:
        while True:
            try:
                user_input = await self.session.prompt_async("> ")
                if not user_input.strip():
                    continue

                response = await self.agent.run(user_input)
                print(f"\nResponse:\n{response}")

            except KeyboardInterrupt:
                break
