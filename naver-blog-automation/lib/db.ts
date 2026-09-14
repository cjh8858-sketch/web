import Database from "better-sqlite3";
import path from "path";
import { CONFIG } from "@/config";

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!db) {
    db = new Database(CONFIG.DB_PATH);
    db.pragma("journal_mode = WAL");
    initSchema();
  }
  return db;
}

function initSchema() {
  const database = getDb();

  // Settings table
  database.exec(`
    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
  `);

  // Jobs table
  database.exec(`
    CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY,
      keyword TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending',
      stage TEXT,
      mode TEXT NOT NULL DEFAULT 'auto',
      inputs TEXT,
      error TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  // Sources table (수집 자료)
  database.exec(`
    CREATE TABLE IF NOT EXISTS sources (
      id TEXT PRIMARY KEY,
      job_id TEXT NOT NULL REFERENCES jobs(id),
      type TEXT NOT NULL,
      title TEXT NOT NULL,
      summary TEXT,
      url TEXT NOT NULL,
      content TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  // Ideas table (글감)
  database.exec(`
    CREATE TABLE IF NOT EXISTS ideas (
      id TEXT PRIMARY KEY,
      job_id TEXT NOT NULL REFERENCES jobs(id),
      title TEXT NOT NULL,
      angle TEXT,
      rationale TEXT,
      chosen INTEGER DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  // Drafts table (초안)
  database.exec(`
    CREATE TABLE IF NOT EXISTS drafts (
      id TEXT PRIMARY KEY,
      job_id TEXT NOT NULL REFERENCES jobs(id),
      idea_id TEXT REFERENCES ideas(id),
      title TEXT NOT NULL,
      body_json TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  // Images table
  database.exec(`
    CREATE TABLE IF NOT EXISTS images (
      id TEXT PRIMARY KEY,
      job_id TEXT NOT NULL REFERENCES jobs(id),
      draft_id TEXT REFERENCES drafts(id),
      query TEXT NOT NULL,
      src_url TEXT,
      local_path TEXT,
      source_site TEXT NOT NULL,
      verdict_ok INTEGER,
      verdict_reason TEXT,
      section_index INTEGER,
      gen_prompt TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  // Posts table (발행된 글)
  database.exec(`
    CREATE TABLE IF NOT EXISTS posts (
      id TEXT PRIMARY KEY,
      job_id TEXT NOT NULL REFERENCES jobs(id),
      draft_id TEXT REFERENCES drafts(id),
      status TEXT NOT NULL DEFAULT 'pending',
      blog_url TEXT,
      screenshot TEXT,
      note TEXT,
      published_at TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  // Job logs
  database.exec(`
    CREATE TABLE IF NOT EXISTS job_logs (
      id TEXT PRIMARY KEY,
      job_id TEXT NOT NULL REFERENCES jobs(id),
      level TEXT NOT NULL DEFAULT 'info',
      message TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);

  // Naver session metadata
  database.exec(`
    CREATE TABLE IF NOT EXISTS naver_session_meta (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      saved_at TEXT,
      is_valid INTEGER DEFAULT 0
    );
  `);
}

// Helper functions
export function runQuery<T>(sql: string, params: any[] = []): T[] {
  const stmt = getDb().prepare(sql);
  return stmt.all(...params) as T[];
}

export function runQueryOne<T>(sql: string, params: any[] = []): T | undefined {
  const stmt = getDb().prepare(sql);
  return stmt.get(...params) as T | undefined;
}

export function runUpdate(sql: string, params: any[] = []): number {
  const stmt = getDb().prepare(sql);
  const result = stmt.run(...params);
  return result.changes;
}

export function closeDb() {
  if (db) {
    db.close();
    db = null;
  }
}
