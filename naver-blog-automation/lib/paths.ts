import fs from "fs";
import path from "path";
import { CONFIG } from "@/config";

export function ensureDataDir() {
  if (!fs.existsSync(CONFIG.DATA_DIR)) {
    fs.mkdirSync(CONFIG.DATA_DIR, { recursive: true });
  }
  if (!fs.existsSync(CONFIG.IMAGES_DIR)) {
    fs.mkdirSync(CONFIG.IMAGES_DIR, { recursive: true });
  }
}

export function normalizePath(p: string): string {
  let norm = path.resolve(p).normalize("NFC");
  if (process.platform === "win32") {
    norm = norm.toLowerCase();
  }
  return norm;
}

export function isPathInDataDir(p: string): boolean {
  const normalized = normalizePath(p);
  const dataDir = normalizePath(CONFIG.DATA_DIR);
  return normalized.startsWith(dataDir + path.sep);
}

export function getImagePath(filename: string): string {
  return path.join(CONFIG.IMAGES_DIR, filename);
}

// Ensure data directory exists
ensureDataDir();
