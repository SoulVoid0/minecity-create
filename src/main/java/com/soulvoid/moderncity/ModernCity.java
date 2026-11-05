package com.soulvoid.moderncity;

import com.mojang.logging.LogUtils;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import org.slf4j.Logger;

import java.util.List;

/**
 * Entry point. The style packs live in src/main/resources/blueprints/moderncity/ and are
 * discovered by Structurize from the jar. This class only logs which pack variant is usable.
 */
@Mod(ModernCity.MOD_ID)
public final class ModernCity {
    public static final String MOD_ID = "moderncity";
    public static final Logger LOG = LogUtils.getLogger();

    /** Mods the full "Modern City" pack needs; without them only "Modern City Lite" is offered. */
    public static final List<String> FULL_PACK_MODS = List.of("create", "ae2", "createaddition");

    /** Extra mods the "Modern City Complete" pack needs on top of FULL_PACK_MODS. */
    public static final List<String> COMPLETE_PACK_MODS = List.of(
            "railways", "tfmg", "createdieselgenerators", "createnuclear", "create_radar", "createoreexcavation",
            "create_new_age", "extendedae", "megacells", "advanced_ae", "appliedcreate", "appgen", "appflux",
            "chipped", "tacz", "cold_sweat", "mcwbridges", "mcwdoors", "mcwfences", "mcwfurnitures", "mcwlights",
            "mcwpaths", "mcwroofs", "mcwstairs", "mcwtrpdoors", "mcwwindows");

    public ModernCity(IEventBus modBus) {
        modBus.addListener(this::commonSetup);
        net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(SelfTest::onServerStarted);
    }

    private void commonSetup(FMLCommonSetupEvent event) {
        List<String> missing = FULL_PACK_MODS.stream().filter(id -> !ModList.get().isLoaded(id)).toList();
        if (missing.isEmpty()) {
            LOG.info("[Modern City] full pack available");
        } else {
            LOG.info("[Modern City] {} not installed, only the Modern City Lite style pack is offered", missing);
        }
        List<String> missingComplete = COMPLETE_PACK_MODS.stream().filter(id -> !ModList.get().isLoaded(id)).toList();
        if (missing.isEmpty() && missingComplete.isEmpty()) {
            LOG.info("[Modern City] Complete pack available");
        } else if (!missingComplete.isEmpty()) {
            LOG.info("[Modern City] Complete pack hidden, missing: {}", missingComplete);
        }
    }
}
