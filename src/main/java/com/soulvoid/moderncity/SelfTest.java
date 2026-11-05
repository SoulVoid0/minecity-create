package com.soulvoid.moderncity;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtAccounter;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.properties.Property;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

/**
 * Dev check, run with -Dmoderncity.selftest=true: re-reads every shipped blueprint against the
 * live block and block-entity registries. A pack only counts if all of its mods are loaded, since
 * Structurize would hide it otherwise. With -Dmoderncity.selftest=exit the server stops afterwards.
 */
final class SelfTest {
    private SelfTest() {
    }

    static void onServerStarted(ServerStartedEvent event) {
        String mode = System.getProperty("moderncity.selftest");
        if (mode == null) {
            return;
        }
        int problems = 0;
        Path root = ModList.get().getModFileById(ModernCity.MOD_ID).getFile().findResource("blueprints", ModernCity.MOD_ID);
        try (Stream<Path> packs = Files.list(root)) {
            for (Path pack : packs.toList()) {
                problems += checkPack(pack);
            }
        } catch (Exception e) {
            ModernCity.LOG.error("[Modern City selftest] could not list packs", e);
            problems++;
        }
        ModernCity.LOG.info("[Modern City selftest] DONE, {} problem(s)", problems);
        if ("exit".equals(mode)) {
            event.getServer().halt(false);
        }
    }

    private static int checkPack(Path pack) throws Exception {
        String packJson = Files.readString(pack.resolve("pack.json"));
        com.google.gson.JsonObject json = com.google.gson.JsonParser.parseString(packJson).getAsJsonObject();
        List<String> missingMods = new ArrayList<>();
        json.getAsJsonArray("mods").forEach(m -> {
            if (!ModList.get().isLoaded(m.getAsString())) {
                missingMods.add(m.getAsString());
            }
        });
        String name = json.get("name").getAsString();
        if (!missingMods.isEmpty()) {
            ModernCity.LOG.info("[Modern City selftest] pack '{}' skipped (Structurize hides it): missing {}", name, missingMods);
            return 0;
        }
        int files = 0;
        int problems = 0;
        try (Stream<Path> walk = Files.walk(pack)) {
            for (Path file : walk.filter(p -> p.toString().endsWith(".blueprint")).toList()) {
                files++;
                problems += checkBlueprint(pack.relativize(file).toString(), file);
            }
        }
        ModernCity.LOG.info("[Modern City selftest] pack '{}': {} blueprints, {} problem(s)", name, files, problems);
        return problems;
    }

    private static int checkBlueprint(String rel, Path file) throws Exception {
        CompoundTag tag;
        try (InputStream in = Files.newInputStream(file)) {
            tag = NbtIo.readCompressed(in, NbtAccounter.unlimitedHeap());
        }
        int problems = 0;
        ListTag palette = tag.getList("palette", Tag.TAG_COMPOUND);
        for (int i = 0; i < palette.size(); i++) {
            CompoundTag entry = palette.getCompound(i);
            ResourceLocation id = ResourceLocation.parse(entry.getString("Name"));
            if (!BuiltInRegistries.BLOCK.containsKey(id)) {
                ModernCity.LOG.warn("[Modern City selftest] {}: unknown block {}", rel, id);
                problems++;
                continue;
            }
            Block block = BuiltInRegistries.BLOCK.get(id);
            CompoundTag props = entry.getCompound("Properties");
            for (String key : props.getAllKeys()) {
                Property<?> prop = block.getStateDefinition().getProperty(key);
                if (prop == null) {
                    ModernCity.LOG.warn("[Modern City selftest] {}: {} has no property '{}'", rel, id, key);
                    problems++;
                } else if (prop.getValue(props.getString(key)).isEmpty()) {
                    ModernCity.LOG.warn("[Modern City selftest] {}: {} bad value {}={}", rel, id, key, props.getString(key));
                    problems++;
                }
            }
        }
        ListTag tes = tag.getList("tile_entities", Tag.TAG_COMPOUND);
        for (int i = 0; i < tes.size(); i++) {
            ResourceLocation id = ResourceLocation.parse(tes.getCompound(i).getString("id"));
            if (!BuiltInRegistries.BLOCK_ENTITY_TYPE.containsKey(id)) {
                ModernCity.LOG.warn("[Modern City selftest] {}: unknown block entity {}", rel, id);
                problems++;
            }
        }
        return problems;
    }
}
