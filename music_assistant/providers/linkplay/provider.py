"""Demo Player Provider implementation."""

from __future__ import annotations

import pywiim
from pywiim import discover_devices

from music_assistant.models.player_provider import PlayerProvider

from .player import LinkPlayPlayer


class LinkPlayPlayerprovider(PlayerProvider):
    """
    Example/demo Player provider.

    Note that this is always subclassed from PlayerProvider,
    which in turn is a subclass of the generic Provider model.

    The base implementation already takes care of some convenience methods,
    such as the mass object and the logger. Take a look at the base class
    for more information on what is available.

    Just like with any other subclass, make sure that if you override
    any of the default methods (such as __init__), you call the super() method.
    In most cases its not needed to override any of the builtin methods and you only
    implement the abc methods with your actual implementation.
    """

    async def handle_async_init(self) -> None:
        """Handle async initialization of the provider."""
        # OPTIONAL
        # this is an optional method that you can implement if
        # relevant or leave out completely if not needed.
        # it will be called when the provider is initialized in Music Assistant.
        # you can use this to do any async initialization of the provider,
        # such as loading configuration, setting up connections, etc.
        self.logger.info("Initializing DemoPlayerProvider with config: %s", self.config)

    async def loaded_in_mass(self) -> None:
        """Call after the provider has been loaded."""
        # OPTIONAL
        # this is an optional method that you can implement if
        # relevant or leave out completely if not needed.
        # it will be called after the provider has been fully loaded into Music Assistant.
        # you can use this for instance to trigger custom (non-mdns) discovery of players
        # or any other logic that needs to run after the provider is fully loaded.
        self.logger.info("DemoPlayerProvider loaded")
        await self.discover_players()

    async def unload(self, is_removed: bool = False) -> None:
        """
        Handle unload/close of the provider.

        Called when provider is deregistered (e.g. MA exiting or config reloading).
        is_removed will be set to True when the provider is removed from the configuration.
        """
        # OPTIONAL
        # this is an optional method that you can implement if
        # relevant or leave out completely if not needed.
        # it will be called when the provider is unloaded from Music Assistant.
        # this means also when the provider is getting reloaded
        for player in self.players:
            # if you have any cleanup logic for the players, you can do that here.
            # e.g. disconnecting from the player, closing connections, etc.
            self.logger.debug("Unloading player %s", player.name)
            await self.mass.players.unregister(player.player_id)

    def on_player_enabled(self, player_id: str) -> None:
        """Call (by config manager) when a player gets enabled."""
        # OPTIONAL
        # this is an optional method that you can implement if
        # you want to do something special when a player is enabled.

    def on_player_disabled(self, player_id: str) -> None:
        """Call (by config manager) when a player gets disabled."""
        # OPTIONAL
        # this is an optional method that you can implement if
        # you want to do something special when a player is disabled.
        # e.g. you can stop polling the player or disconnect from it.

    async def remove_player(self, player_id: str) -> None:
        """Remove a player from this provider."""
        # OPTIONAL - required only if you specified ProviderFeature.REMOVE_PLAYER
        # this is used to actually remove a player.

    async def discover_players(self) -> None:
        """Discover players for this provider."""
        # This is an optional method that you can implement if
        # you want to (manually) discover players on the
        # network and you do not use mdns discovery.
        devices = await discover_devices()

        uuid = ""

        def on_state_changed():
            if not (mass_player := self.mass.players.get(uuid)):
                return  # guard for unknown player
            mass_player.on_state_changed()

        wiimplayer = pywiim.Player(
            pywiim.WiiMClient("192.168.1.109"), on_state_changed=on_state_changed
        )

        await wiimplayer.refresh()

        uuid = wiimplayer.uuid

        player = LinkPlayPlayer(provider=self, player_id=wiimplayer.uuid, wiimplayer=wiimplayer)

        await self.mass.players.register(player)

        for device in devices:
            self.logger.info(f"Found {device.name} @ {device.ip}")
            # print(f"Found: {device.name} @ {device.ip}")
            # print(f"  Model: {device.model}")
            # print(f"  Firmware: {device.firmware}")
            # print(f"  Vendor: {device.vendor}")

            # player = LinkPlayPlayer(
            #     provider=self,
            #     player_id=f"demo_{i}",
            # )
            # # register the player with the player manager
            # await self.mass.players.register(player)

            # once the player is registered, you can either instruct the player manager to
            # poll the player for state changes or you can implement your own logic to
            # listen for state changes from the player and update the player object accordingly.
            # if the player state needs to be updated, you can call the update method on the player:
            # player.update_state()
