import { z } from "zod";

// Job status
export const JobStatusSchema = z.enum([
  "pending",
  "scraping",
  "writing",
  "imaging",
  "publishing",
  "done",
  "failed",
  "canceled",
]);

// Job mode (content type)
export const JobModeSchema = z.enum(["auto", "experience", "branding"]);

// Post status
export const PostStatusSchema = z.enum([
  "pending",
  "publishing",
  "published",
  "dry_run",
  "failed",
  "blocked",
]);

// Image source
export const ImageSourceSchema = z.enum(["naver", "google", "ai", "local"]);

// Visibility (공개 범위)
export const VisibilitySchema = z.enum(["public", "neighbor", "both", "private"]);

// Settings key
export const SettingsKeySchema = z.enum([
  "dryRun",
  "killSwitch",
  "visibility",
  "dailyPublishLimit",
  "minPublishIntervalMin",
  "scrapeTopN",
  "imageCandidates",
  "cfImageSteps",
  "showBrowser",
  "claudeTimeoutSec",
  "claudeConcurrency",
  "naver_blog_id",
  "unsplash_key",
  "pixabay_key",
  "cloudflare_account_id",
  "cloudflare_api_token",
]);

// Draft section types
export const SectionSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("heading"),
    text: z.string(),
  }),
  z.object({
    type: z.literal("paragraph"),
    text: z.string(),
    highlight: z.string().optional(),
  }),
  z.object({
    type: z.literal("quote"),
    text: z.string(),
  }),
  z.object({
    type: z.literal("divider"),
  }),
  z.object({
    type: z.literal("image"),
    query: z.string(),
    caption: z.string().optional(),
  }),
]);

export const DraftSchema = z.object({
  title: z.string(),
  sections: z.array(SectionSchema).min(6, "최소 6개 섹션 필요"),
  tags: z.array(z.string()).optional(),
});

// Job
export const JobSchema = z.object({
  id: z.string(),
  keyword: z.string(),
  status: JobStatusSchema,
  stage: z.string().optional(),
  mode: JobModeSchema,
  inputs: z.record(z.any()).optional(),
  error: z.string().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

// Settings
export const SettingSchema = z.object({
  key: SettingsKeySchema,
  value: z.string(),
});

// Settings object (all settings)
export const AllSettingsSchema = z.record(
  z.string(),
  z.union([z.string(), z.number(), z.boolean()])
);

// Source (수집 자료)
export const SourceSchema = z.object({
  id: z.string(),
  job_id: z.string(),
  type: z.enum(["news", "blog"]),
  title: z.string(),
  summary: z.string(),
  url: z.string(),
  content: z.string().optional(),
  created_at: z.string(),
});

// Idea (글감)
export const IdeaSchema = z.object({
  id: z.string(),
  job_id: z.string(),
  title: z.string(),
  angle: z.string(),
  rationale: z.string(),
  chosen: z.boolean(),
  created_at: z.string(),
});

// Image
export const ImageSchema = z.object({
  id: z.string(),
  job_id: z.string(),
  draft_id: z.string().optional(),
  query: z.string(),
  src_url: z.string().optional(),
  local_path: z.string().optional(),
  source_site: ImageSourceSchema,
  verdict_ok: z.boolean().optional(),
  verdict_reason: z.string().optional(),
  section_index: z.number().optional(),
  gen_prompt: z.string().optional(),
  created_at: z.string(),
});

// Post (발행된 글)
export const PostSchema = z.object({
  id: z.string(),
  job_id: z.string(),
  draft_id: z.string().optional(),
  status: PostStatusSchema,
  blog_url: z.string().optional(),
  screenshot: z.string().optional(),
  note: z.string().optional(),
  published_at: z.string().optional(),
  created_at: z.string(),
});

// Job log
export const JobLogSchema = z.object({
  id: z.string(),
  job_id: z.string(),
  level: z.enum(["debug", "info", "warn", "error"]),
  message: z.string(),
  created_at: z.string(),
});

// API responses
export const ApiStatusResponseSchema = z.object({
  success: z.boolean(),
  claude_version: z.string().optional(),
  naver_session_valid: z.boolean(),
  cloudflare_configured: z.boolean(),
  settings: AllSettingsSchema,
});

export const ApiJobResponseSchema = z.object({
  success: z.boolean(),
  data: JobSchema.optional(),
  error: z.string().optional(),
});

// Types export
export type JobStatus = z.infer<typeof JobStatusSchema>;
export type JobMode = z.infer<typeof JobModeSchema>;
export type PostStatus = z.infer<typeof PostStatusSchema>;
export type ImageSource = z.infer<typeof ImageSourceSchema>;
export type Visibility = z.infer<typeof VisibilitySchema>;
export type Section = z.infer<typeof SectionSchema>;
export type Draft = z.infer<typeof DraftSchema>;
export type Job = z.infer<typeof JobSchema>;
export type Setting = z.infer<typeof SettingSchema>;
export type AllSettings = z.infer<typeof AllSettingsSchema>;
export type Source = z.infer<typeof SourceSchema>;
export type Idea = z.infer<typeof IdeaSchema>;
export type Image = z.infer<typeof ImageSchema>;
export type Post = z.infer<typeof PostSchema>;
export type JobLog = z.infer<typeof JobLogSchema>;
