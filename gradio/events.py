"""Contains all of the events that can be triggered in a gr.Blocks() app, with the exception
of the on-page-load event, which is defined in gr.Blocks().load()."""

from __future__ import annotations

from functools import partial, wraps
from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence

from gradio_client.documentation import document

if TYPE_CHECKING:
    from gradio.blocks import Block, Component

from gradio.deprecation import warn_deprecation
from gradio.utils import get_cancel_function


def set_cancel_events(
    block: Block, event_name: str, cancels: None | dict[str, Any] | list[dict[str, Any]]
):
    if cancels:
        if not isinstance(cancels, list):
            cancels = [cancels]
        cancel_fn, fn_indices_to_cancel = get_cancel_function(cancels)
        block.set_event_trigger(
            event_name,
            cancel_fn,
            inputs=None,
            outputs=None,
            queue=False,
            preprocess=False,
            cancels=fn_indices_to_cancel,
        )


class Dependency(dict):
    def __init__(self, trigger: Block, key_vals, dep_index, fn):
        super().__init__(key_vals)
        self.fn = fn
        self.trigger = trigger
        self.then = partial(
            EventListener(
                "then",
                trigger_after=dep_index,
                trigger_only_on_success=False,
            ).listener,
            trigger,
        )
        """
        Triggered after directly preceding event is completed, regardless of success or failure.
        """
        self.success = partial(
            EventListener(
                "success",
                trigger_after=dep_index,
                trigger_only_on_success=True,
            ).listener,
            trigger,
        )
        """
        Triggered after directly preceding event is completed, if it was successful.
        """

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


@document()
class EventData:
    """
    When a subclass of EventData is added as a type hint to an argument of an event listener method, this object will be passed as that argument.
    It contains information about the event that triggered the listener, such the target object, and other data related to the specific event that are attributes of the subclass.

    Example:
        table = gr.Dataframe([[1, 2, 3], [4, 5, 6]])
        gallery = gr.Gallery([("cat.jpg", "Cat"), ("dog.jpg", "Dog")])
        textbox = gr.Textbox("Hello World!")

        statement = gr.Textbox()

        def on_select(evt: gr.SelectData):  # SelectData is a subclass of EventData
            return f"You selected {evt.value} at {evt.index} from {evt.target}"

        table.select(on_select, None, statement)
        gallery.select(on_select, None, statement)
        textbox.select(on_select, None, statement)
    Demos: gallery_selections, tictactoe
    """

    def __init__(self, target: Block | None, _data: Any):
        """
        Parameters:
            target: The target object that triggered the event. Can be used to distinguish if multiple components are bound to the same listener.
        """
        self.target = target
        self._data = _data


class SelectData(EventData):
    def __init__(self, target: Block | None, data: Any):
        super().__init__(target, data)
        self.index: int | tuple[int, int] = data["index"]
        """
        The index of the selected item. Is a tuple if the component is two dimensional or selection is a range.
        """
        self.value: Any = data["value"]
        """
        The value of the selected item.
        """
        self.selected: bool = data.get("selected", True)
        """
        True if the item was selected, False if deselected.
        """


class EventListener(str):
    def __new__(cls, event_name, *args, **kwargs):
        return super().__new__(cls, event_name)

    def __init__(
        self,
        event_name: str,
        show_progress: Literal["full", "minimal", "hidden"] | None = None,
        callback: Callable | None = None,
        trigger_after: int | None = None,
        trigger_only_on_success: bool = False,
    ):
        super().__init__()
        self.event_name = event_name
        self.show_progress = show_progress
        self.trigger_after = trigger_after
        self.trigger_only_on_success = trigger_only_on_success
        self.callback = callback
        self.listener = self._setup(
            event_name, show_progress, callback, trigger_after, trigger_only_on_success
        )

    @staticmethod
    def _setup(
        _event_name: str,
        _show_progress: Literal["full", "minimal", "hidden"] | None,
        _callback: Callable | None,
        _trigger_after: int | None,
        _trigger_only_on_success: bool,
    ):
        def event_trigger(
            block: Block,
            fn: Callable | None,
            inputs: Component | Sequence[Component] | set[Component] | None = None,
            outputs: Component | Sequence[Component] | None = None,
            api_name: str | None | Literal[False] = None,
            status_tracker: None = None,
            scroll_to_output: bool = False,
            show_progress: Literal["full", "minimal", "hidden"] = "full",
            queue: bool | None = None,
            batch: bool = False,
            max_batch_size: int = 4,
            preprocess: bool = True,
            postprocess: bool = True,
            cancels: dict[str, Any] | list[dict[str, Any]] | None = None,
            every: float | None = None,
            _js: str | None = None,
        ) -> Dependency:
            """
            Parameters:
                fn: the function to call when this event is triggered. Often a machine learning model's prediction function. Each parameter of the function corresponds to one input component, and the function should return a single value or a tuple of values, with each element in the tuple corresponding to one output component.
                inputs: List of gradio.components to use as inputs. If the function takes no inputs, this should be an empty list.
                outputs: List of gradio.components to use as outputs. If the function returns no outputs, this should be an empty list.
                api_name: Defines how the endpoint appears in the API docs. Can be a string, None, or False. If False, the endpoint will not be exposed in the api docs. If set to None, the endpoint will be exposed in the api docs as an unnamed endpoint, although this behavior will be changed in Gradio 4.0. If set to a string, the endpoint will be exposed in the api docs with the given name.
                status_tracker: Deprecated and has no effect.
                scroll_to_output: If True, will scroll to output component on completion
                show_progress: If True, will show progress animation while pending
                queue: If True, will place the request on the queue, if the queue has been enabled. If False, will not put this event on the queue, even if the queue has been enabled. If None, will use the queue setting of the gradio app.
                batch: If True, then the function should process a batch of inputs, meaning that it should accept a list of input values for each parameter. The lists should be of equal length (and be up to length `max_batch_size`). The function is then *required* to return a tuple of lists (even if there is only 1 output component), with each list in the tuple corresponding to one output component.
                max_batch_size: Maximum number of inputs to batch together if this is called from the queue (only relevant if batch=True)
                preprocess: If False, will not run preprocessing of component data before running 'fn' (e.g. leaving it as a base64 string if this method is called with the `Image` component).
                postprocess: If False, will not run postprocessing of component data before returning 'fn' output to the browser.
                cancels: A list of other events to cancel when this listener is triggered. For example, setting cancels=[click_event] will cancel the click_event, where click_event is the return value of another components .click method. Functions that have not yet run (or generators that are iterating) will be cancelled, but functions that are currently running will be allowed to finish.
                every: Run this event 'every' number of seconds while the client connection is open. Interpreted in seconds. Queue must be enabled.
            """

            if fn == "decorator":
                def wrapper(func):
                    event_trigger(
                        block,
                        func,
                        inputs,
                        outputs,
                        api_name,
                        status_tracker,
                        scroll_to_output,
                        show_progress,
                        queue,
                        batch,
                        max_batch_size,
                        preprocess,
                        postprocess,
                        cancels,
                        every,
                        _js,
                    )

                    @wraps(func)
                    def inner(*args, **kwargs):
                        return func(*args, **kwargs)

                    return inner

                return Dependency(None, {}, None, wrapper)


            if status_tracker:
                warn_deprecation(
                    "The 'status_tracker' parameter has been deprecated and has no effect."
                )
            if _event_name == "stop":
                warn_deprecation(
                    "The `stop` event on Video and Audio has been deprecated and will be remove in a future version. Use `ended` instead."
                )
            if "stream" in block.events:
                block.check_streamable()
            if isinstance(show_progress, bool):
                show_progress = "full" if show_progress else "hidden"

            dep, dep_index = block.set_event_trigger(
                _event_name,
                fn,
                inputs,
                outputs,
                preprocess=preprocess,
                postprocess=postprocess,
                scroll_to_output=scroll_to_output,
                show_progress=show_progress
                if show_progress is not None
                else _show_progress,
                api_name=api_name,
                js=_js,
                queue=queue,
                batch=batch,
                max_batch_size=max_batch_size,
                every=every,
                trigger_after=_trigger_after,
                trigger_only_on_success=_trigger_only_on_success,
            )
            set_cancel_events(block, _event_name, cancels)
            if _callback:
                _callback(block)
            return Dependency(block, dep, dep_index, fn)

        return event_trigger


class Events:
    change = "change"
    input = "input"
    click = "click"
    submit = "submit"
    edit = "edit"
    clear = "clear"
    play = "play"
    pause = "pause"
    stop = "stop"
    end = "end"
    start_recording = "start_recording"
    stop_recording = "stop_recording"
    focus = "focus"
    blur = "blur"
    upload = "upload"
    release = "release"
    select = EventListener(
        "select", callback=lambda block: setattr(block, "selectable", True)
    )
    stream = EventListener(
        "stream",
        show_progress="hidden",
        callback=lambda block: setattr(block, "streaming", True),
    )
    like = EventListener(
        "like",
        callback=lambda block: setattr(block, "likeable", True)
    )


class LikeData(EventData):
    def __init__(self, target: Block | None, data: Any):
        super().__init__(target, data)
        self.index: int | tuple[int, int] = data["index"]
        """
        The index of the liked/disliked item. Is a tuple if the component is two dimensional.
        """
        self.value: Any = data["value"]
        """
        The value of the liked/disliked item.
        """
        self.liked: bool = data.get("liked", True)
        """
        True if the item was liked, False if disliked.
        """
