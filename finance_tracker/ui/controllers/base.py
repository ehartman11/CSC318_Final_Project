from __future__ import annotations


class Controller:
    """Common interface for controllers."""
    def bind(self) -> None:
        """Connect view signals to controller slots."""
        raise NotImplementedError

    def refresh(self) -> None:
        """Refresh the view from the model/service."""
        pass

    def dispose(self) -> None:
        """Disconnect signals if needed."""
        pass
