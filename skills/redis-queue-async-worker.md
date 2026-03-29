---
name: Redis Queue Async Worker
description: Master Redis-based async job queue patterns for decoupling services. Covers BullMQ, Sidekiq, and Celery equivalents in Rust/TypeScript with protobuf serialization, retries, DLQ, priority, deduplication, rate limiting, graceful shutdown, health checks, and monitoring.
tags: [redis, queue, async, bullmq, sidekiq, celery, rust, tokio, typescript, job-queue, distributed-systems]
icon: 📬
category: messaging
version: 1.0.0
eval_cases:
  - id: proto_serialization
    prompt: |
      Write a Rust function using tokio and redis-rs that serializes a job payload to Protocol Buffers binary format (not JSON!) before enqueueing. Include the proto message definition for a generic Job { id, type, payload, created_at, retries }. Show enqueue and dequeue functions.
    checks:
      - regex: "prost|prost_build|protobuf"
        description: Must use protobuf serialization
      - regex: "Binary|serialize_to_vec|encode"
        description: Binary encoding (not JSON/text)
      - regex: "Job\\s*\\{|message Job"
        description: Job struct/message defined
      - regex: "redis::cmd|lrange|brpoplpush"
        description: Redis list operations for queue
    expectations:
      - Uses prost for protobuf codegen
      - encode_to_vec or similar for binary serialization
      - Shows both enqueue and dequeue logic
      - Includes error handling

  - id: exponential_backoff_retry
    prompt: |
      Implement retry logic with exponential backoff for a Rust async worker. Job should retry up to 5 times with jitter. Calculate delay as min(base * 2^attempt + random_jitter, max_delay). Show how to track attempt count in job metadata and when to move to DLQ.
    checks:
      - regex: "attempt|retries"
        description: Tracks retry attempts
      - regex: "exponential|2\\^|pow|\\*\\s*2"
        description: Exponential backoff calculation
      - regex: "jitter|rand|random"
        description: Jitter for thundering herd prevention
      - regex: "dead.?letter|DLQ|failed"
        description: DLQ handling for exhausted retries
      - regex: "tokio::time::sleep|duration"
        description: Async delay implementation
    expectations:
      - Backoff formula: base * 2^attempt with jitter
      - Max delay cap
      - Max 5 retry attempts
      - Moves to DLQ after exhausted retries
      - Non-blocking async sleep

  - id: bullmq_priority_queue
    prompt: |
      Create a TypeScript BullMQ setup with 3 priority levels (high=1, normal=5, low=10). Show how to add jobs with priority, configure worker to process in priority order, and how to change job priority after enqueueing using Job.update().
    checks:
      - regex: "Queue|Worker|QueueEvents"
        description: BullMQ core components
      - regex: "priority|Priority"
        description: Priority queue configuration
      - regex: "job\\.update|updateOptions"
        description: Dynamic priority update
      - regex: "maxLen|listMaxLength"
        description: Bounded queue size
    expectations:
      - Three distinct priority levels
      - Worker processes high priority first
      - Can update job priority post-enqueue
      - Queue options properly configured

  - id: job_deduplication
    prompt: |
      Implement job deduplication in Rust using Redis SETNX or SET with NX and EX flags. Show how to prevent duplicate jobs based on a unique key (e.g., user_id + job_type + idempotency_key). Include TTL for the deduplication lock.
    checks:
      - regex: "SETNX|SetNX|set.*NX|set_nx"
        description: Redis atomic set-if-not-exists
      - regex: "EX|ex|TTL|expire"
        description: TTL for lock expiration
      - regex: "idempoten|dedup|duplicate"
        description: Deduplication logic
      - regex: "lock|unique.?key"
        description: Unique lock/key mechanism
    expectations:
      - Atomic SET with NX flag
      - TTL on deduplication key
      - Returns boolean indicating if job was new
      - Handles race conditions

  - id: rate_limiting
    prompt: |
      Write a BullMQ rate limiter in TypeScript using a sliding window algorithm. Limit to 100 jobs per minute globally. Show how to check rate limit before adding jobs and how to handle 429 responses gracefully with retry-after.
    checks:
      - regex: "rateLimit|RateLimiter|limiter"
        description: Rate limiting implementation
      - regex: "window|sliding|minute|100"
        description: Sliding window or fixed window
      - regex: "limiter\\.addJob|add"
        description: Rate-limited job addition
      - regex: "429|retryAfter|backoff"
        description: Rate limit exceeded handling
    expectations:
      - 100 jobs/minute limit enforced
      - Sliding window or token bucket pattern
      - Graceful handling when limit hit
      - Uses BullMQ built-in limiter or custom Redis

  - id: dead_letter_queue
    prompt: |
      Configure a Rust worker to move failed jobs to a dead letter queue after all retries are exhausted. Show: 1) DLQ queue setup, 2) moving job with full metadata, 3) DLQ processor for manual inspection/requeue, 4) metrics for DLQ size.
    checks:
      - regex: "dead.?letter|DLQ|failed_jobs"
        description: DLQ configuration
      - regex: "move|copy|transfer|brpoplpush"
        description: Job movement to DLQ
      - regex: "metadata|attempts|error|stack"
        description: Preserves job metadata
      - regex: "metrics|len|LLEN"
        description: DLQ size monitoring
      - regex: "requeue|retry|replay"
        description: DLQ job reprocessing
    expectations:
      - Separate DLQ list in Redis
      - Full metadata preserved on move
      - DLQ processor for manual intervention
      - Monitoring/alerting on DLQ growth

  - id: graceful_shutdown
    prompt: |
      Implement graceful shutdown for a Rust tokio worker handling Redis queues. Requirements: 1) Catch SIGTERM/SIGINT, 2) Stop accepting new jobs, 3) Wait for in-flight jobs to complete (with timeout), 4) Close Redis connections cleanly. Use shutdown signal handling.
    checks:
      - regex: "SIGTERM|SIGINT|signal|ctrl_c"
        description: Signal handling
      - regex: "shutdown|graceful|drain"
        description: Graceful shutdown orchestration
      - regex: "in.?flight|pending|processing"
        description: In-flight job tracking
      - regex: "timeout|duration|elapsed"
        description: Shutdown timeout
      - regex: "close|drop|disconnect"
        description: Clean connection teardown
    expectations:
      - Signal handlers for SIGTERM/SIGINT
      - Stops new job polling
      - Waits for in-flight with timeout
      - Clean Redis connection close
      - Returns exit code 0 on success

  - id: health_check_endpoint
    prompt: |
      Create a health check endpoint for a Redis queue worker in both Rust (Actix-web) and TypeScript (Express). Check: 1) Redis connectivity (PING), 2) Queue depth (LLEN), 3) Worker active status, 4) Memory/connection pool health. Return proper status codes and JSON response.
    checks:
      - regex: "ping|PING|pingpong"
        description: Redis ping check
      - regex: "LLEN|len|depth|size"
        description: Queue depth check
      - regex: "healthy|status|up|down"
        description: Health status response
      - regex: "connection|pool|Client"
        description: Connection pool status
      - regex: "actix|express|HttpServer"
        description: HTTP framework integration
    expectations:
      - Redis PING command
      - Queue length monitoring
      - Degraded/unhealthy distinction
      - JSON health response
      - Works with load balancers

  - id: monitoring_metrics
    prompt: |
      Export Prometheus metrics from a Rust async worker: jobs_enqueued_total, jobs_completed_total, jobs_failed_total, job_duration_seconds (histogram), queue_depth (gauge), active_workers (gauge), retry_count histogram. Use the opentelemetry or prometheus crate.
    checks:
      - regex: "jobs_enqueued|jobs_completed|jobs_failed"
        description: Job counters
      - regex: "duration|histogram|observe"
        description: Latency histogram
      - regex: "queue_depth|depth|gauge"
        description: Queue depth gauge
      - regex: "active_workers|workers|gauge"
        description: Active worker gauge
      - regex: "prometheus|opentelemetry|metrics"
        description: Metrics exposition
    expectations:
      - Prometheus counter for job counts
      - Histogram for job duration
      - Gauge for queue depth and workers
      - /metrics endpoint
      - Labels for job type/queue name

  - id: sidekiq_pattern_rust
    prompt: |
      Implement a Sidekiq-style worker pattern in Rust with: 1) Reliable job fetching using BRPOPLPUSH to a processing list, 2) Heartbeat mechanism (re-add to processing with extended TTL), 3) Automatic job resurrection if worker crashes, 4) Middleware chain (before\_enqueue, before\_perform, after\_perform, around\_perform).
    checks:
      - regex: "brpoplpush|BRPOPLPUSH"
        description: Reliable queue fetch
      - regex: "heartbeat|beat|extend|ttl"
        description: Heartbeat mechanism
      - regex: "crash|die| resurrect|orphan"
        description: Crash recovery/resurrection
      - regex: "middleware|before|after|around"
        description: Middleware hooks
      - regex: "performing|perform|execute"
        description: Job execution
    expectations:
      - BRPOPLPUSH to processing queue
      - Heartbeat extends job visibility timeout
      - Orphaned jobs auto-requeued on restart
      - Middleware hooks for extensibility
      - Rust async/await compatible

  - id: celery_eta_retry
    prompt: |
      Build Celery-style ETA (estimated time of arrival) and countdown delay in TypeScript using BullMQ. Support: 1) delayed jobs with countdown seconds, 2) jobs scheduled for specific datetime (eta), 3) retry until datetime with max_retries, 4) show how delayed jobs bypass rate limits.
    checks:
      - regex: "delay|countdown|eta|schedule"
        description: Delayed/ETA job support
      - regex: "postpone|delayed|future"
        description: Future job execution
      - regex: "getState|state|pending|retry"
        description: Job state inspection
      - regex: "remove|cancel|revoke"
        description: Cancel delayed job
      - regex: "delay.*rate|rate.?limit.*delay"
        description: Bypass rate limit for delayed
    expectations:
      - countdown option for seconds delay
      - eta option for specific datetime
      - Can cancel/revoke delayed jobs
      - Delayed jobs don't count vs rate limit
      - Proper ISO datetime parsing

examples:
  - title: Rust Worker with Protobuf + Exponential Backoff
    language: rust
    code: |
      // proto/job.proto
      // syntax = "proto3";
      // message Job {
      //   string id = 1;
      //   string job_type = 2;
      //   bytes payload = 3;
      //   int64 created_at = 4;
      //   int32 retries = 5;
      //   int32 max_retries = 6;
      // }

      use prost::Message;
      use redis::{AsyncCommands, Client};
      use tokio::time::{sleep, Duration};

      #[derive(Message)]
      pub struct Job {
          #[prost(string, tag = "1")]
          pub id: String,
          #[prost(string, tag = "2")]
          pub job_type: String,
          #[prost(bytes, tag = "3")]
          pub payload: Vec<u8>,
          #[prost(int64, tag = "4")]
          pub created_at: i64,
          #[prost(int32, tag = "5")]
          pub retries: i32,
          #[prost(int32, tag = "6")]
          pub max_retries: i32,
      }

      pub async fn enqueue_job(
          redis: &mut redis::aio::MultiplexedConnection,
          queue: &str,
          job: &Job,
      ) -> Result<(), Box<dyn std::error::Error>> {
          let encoded = job.encode_to_vec();
          redis.rpush(format!("queue:{}", queue), encoded).await?;
          Ok(())
      }

      pub async fn process_with_backoff<F, Fut>(
          redis: &mut redis::aio::MultiplexedConnection,
          queue: &str,
          handler: F,
      ) -> Result<(), Box<dyn std::error::Error>>
      where
          F: Fn(Job) Fut,
          Fut: std::future::Future<Output = Result<(), Box<dyn std::error::Error>>>,
      {
          let dlq = format!("queue:{}_dlq", queue);
          let processing_key = format!("processing:{}", queue);
          let backoff_base = Duration::from_secs(1);
          let backoff_max = Duration::from_secs(300);

          loop {
              let (job_bytes, _): (Vec<u8>, Option<String>) =
                  redis.brpoplpush(format!("queue:{}", queue), &processing_key, 5).await?;

              if job_bytes.is_empty() {
                  continue;
              }

              let mut job = Job::decode(job_bytes.as_slice())?;
              let attempt = job.retries;

              match handler(job.clone()).await {
                  Ok(()) => {
                      redis.lrem(&processing_key, 1, &job_bytes).await?;
                  }
                  Err(e) => {
                      if attempt >= job.max_retries {
                          // Move to DLQ
                          redis.lrem(&processing_key, 1, &job_bytes).await?;
                          redis.rpush(&dlq, &job_bytes).await?;
                      } else {
                          // Exponential backoff with jitter
                          let jitter = Duration::from_millis(rand::random::<u64>() % 1000);
                          let delay = (backoff_base * 2u32.pow(attempt as u32)).min(backoff_max) + jitter;
                          
                          job.retries += 1;
                          let updated = job.encode_to_vec();
                          
                          redis.lrem(&processing_key, 1, &job_bytes).await?;
                          sleep(delay).await;
                          redis.rpush(format!("queue:{}", queue), updated).await?;
                      }
                  }
              }
          }
      }

  - title: BullMQ TypeScript with Priority, Rate Limit, and Graceful Shutdown
    language: typescript
    code: |
      import { Queue, Worker, QueueEvents, RateLimiter, FlowProducer } from 'bullmq';
      import Redis from 'ioredis';
      import express, { Request, Response } from 'express';

      const redisOptions = { host: 'localhost', port: 6379 };
      const connection = new Redis(redisOptions);

      // Priority Queue Setup
      const orderQueue = new Queue('order-processing', {
          connection,
          defaultJobOptions: {
              priority: 5,
              attempts: 5,
              backoff: {
                  type: 'exponential',
                  delay: 1000,
              },
          },
      });

      // Rate Limiter (100 jobs per minute)
      const rateLimiter = new RateLimiter({
          limiter: {
              max: 100,
              duration: 60 * 1000, // 1 minute
              strategy: RateLimiter.STRATEGY_SLIDING_WINDOW,
          },
      });

      // Worker with priority
      const orderWorker = new Worker(
          'order-processing',
          async (job) => {
              console.log(`Processing job ${job.id} with priority ${job.opts.priority}`);
              await processOrder(job.data);
          },
          {
              connection,
              concurrency: 10,
          }
      );

      // Queue Events for monitoring
      const queueEvents = new QueueEvents('order-processing', { connection });
      queueEvents.on('completed', ({ jobId }) => console.log(`Job ${jobId} completed`));
      queueEvents.on('failed', ({ jobId, failedReason }) => {
          console.error(`Job ${jobId} failed: ${failedReason}`);
      });

      // Health check endpoint
      const app = express();
      app.get('/health', async (req: Request, res: Response) => {
          const [redisPing, queueCount, activeCount] = await Promise.all([
              connection.ping(),
              orderQueue.getWaitingCount(),
              orderWorker.getActiveCount(),
          ]);

          const healthy = redisPing === 'PONG' && activeCount >= 0;
          res.status(healthy ? 200 : 503).json({
              status: healthy ? 'healthy' : 'unhealthy',
              redis: redisPing,
              queueDepth: queueCount,
              activeWorkers: activeCount,
          });
      });

      // Metrics endpoint for Prometheus
      app.get('/metrics', async (req: Request, res: Response) => {
          const [waiting, active, completed, failed, delayed] = await Promise.all([
              orderQueue.getWaitingCount(),
              orderQueue.getActiveCount(),
              orderQueue.getCompletedCount(),
              orderQueue.getFailedCount(),
              orderQueue.getDelayedCount(),
          ]);

          const metrics = `
              # HELP jobs_enqueued_total Total jobs enqueued
              # TYPE jobs_enqueued_total counter
              jobs_enqueued_total{queue="order-processing"} ${waiting + active + completed + failed + delayed}
              
              # HELP jobs_completed_total Jobs completed successfully
              # TYPE jobs_completed_total counter
              jobs_completed_total{queue="order-processing"} ${completed}
              
              # HELP jobs_failed_total Jobs failed
              # TYPE jobs_failed_total counter
              jobs_failed_total{queue="order-processing"} ${failed}
              
              # HELP queue_depth_current Current jobs waiting
              # TYPE queue_depth_current gauge
              queue_depth_current{queue="order-processing"} ${waiting}
              
              # HELP active_workers Current active workers
              # TYPE active_workers gauge
              active_workers{queue="order-processing"} ${active}
          `;
          res.set('Content-Type', 'text/plain').send(metrics);
      });

      // Graceful Shutdown
      let isShuttingDown = false;
      const shutdown = async () => {
          if (isShuttingDown) return;
          isShuttingDown = true;
          console.log('Graceful shutdown initiated...');

          await orderWorker.close();
          await orderQueue.close();
          await connection.quit();
          
          console.log('Shutdown complete');
          process.exit(0);
      };

      process.on('SIGTERM', shutdown);
      process.on('SIGINT', shutdown);

      // Add jobs with priority
      async function enqueueOrder(orderData: any, priority: number = 5) {
          return orderQueue.add('process-order', orderData, { priority });
      }

      // Delayed/ETA job
      async function scheduleOrder(orderData: any, eta: Date) {
          const delay = eta.getTime() - Date.now();
          return orderQueue.add('process-order', orderData, { delay });
      }

      // Update job priority
      async function updatePriority(jobId: string, newPriority: number) {
          const job = await orderQueue.getJob(jobId);
          await job.update({
              ...job.data,
              priority: newPriority,
          });
      }

      // Job deduplication using unique key
      async function enqueueUnique(idempotencyKey: string, data: any) {
          const existing = await orderQueue.getJobs({
              waiting: true,
          });
          
          const alreadyQueued = existing.some(
              (job) => job.opts.jobId === idempotencyKey
          );
          
          if (alreadyQueued) {
              return null;
          }
          
          return orderQueue.add('process-order', data, {
              jobId: idempotencyKey,
              attempts: 3,
          });
      }

      app.listen(3000);

  - title: Sidekiq-style Reliable Queue in Rust
    language: rust
    code: |
      use redis::{AsyncCommands, Client};
      use std::sync::atomic::{AtomicBool, Ordering};
      use std::sync::Arc;
      use tokio::sync::broadcast;
      use tokio::time::{interval, Duration};

      pub struct SidekiqWorker {
          redis: redis::aio::MultiplexedConnection,
          queue: String,
          processing_key: String,
          heartbeat_ttl: u64,
          shutdown_rx: broadcast::Receiver<()>,
      }

      impl SidekiqWorker {
          pub async fn new(
              redis_url: &str,
              queue: &str,
              heartbeat_ttl: u64,
          ) -> Result<Self, redis::RedisError> {
              let client = Client::open(redis_url)?;
              let redis = client.get_multiplexed_async_connection().await?;
              
              let (shutdown_rx, _) = broadcast::channel(1);
              
              Ok(Self {
                  redis,
                  queue: queue.to_string(),
                  processing_key: format!("sidekiq:processing:{}", queue),
                  heartbeat_ttl,
                  shutdown_rx,
              }) {}
          }

          pub async fn run<M>(&mut self, middleware: M) -> Result<(), Box<dyn std::error::Error + Send + Sync>>
          where
              M: Middleware,
          {
              let mut ticker = interval(Duration::from_secs(5));
              let mut shutdown = self.shutdown_rx.resubscribe();

              loop {
                  tokio::select! {
                      _ = ticker.tick() => {
                          self.heartbeat().await?;
                          self.process_batch(&middleware).await?;
                      }
                      _ = shutdown.recv() => {
                          println!("Shutdown signal received, finishing in-flight jobs...");
                          self.process_batch(&middleware).await?;
                          break;
                      }
                  }
              }
              
              Ok(())
          }

          async fn heartbeat(&mut self) -> Result<(), redis::RedisError> {
              let processing: Vec<(String, String)> = redis::cmd("HGETALL")
                  .query_async(&mut self.redis)
                  .await?;

              let now = std::time::SystemTime::now()
                  .duration_since(std::time::UNIX_EPOCH)
                  .unwrap()
                  .as_secs();

              for (job_key, added_at) in processing {
                  let age: u64 = added_at.parse().unwrap_or(0);
                  if now - age > self.heartbeat_ttl {
                      // Job has been processing too long, move back to queue
                      let job_data: Vec<u8> = redis::cmd("GET")
                          .arg(&job_key)
                          .query_async(&mut self.redis)
                          .await?;
                      
                      if !job_data.is_empty() {
                          self.redis.lpush(&format!("queue:{}", self.queue), &job_data).await?;
                          self.redis.del(&job_key).await?;
                          self.redis.hdel(&self.processing_key, &job_key).await?;
                      }
                  } else {
                      // Extend TTL
                      self.redis.expire(&job_key, self.heartbeat_ttl as i64).await?;
                  }
              }
              
              Ok(())
          }

          async fn process_batch<M>(&mut self, middleware: &M) -> Result<(), Box<dyn std::error::Error + Send + Sync>>
          where
              M: Middleware,
          {
              let result: Vec<Vec<u8>> = redis::cmd("LRANGE")
                  .arg(&format!("queue:{}", self.queue))
                  .arg(0)
                  .arg(9)
                  .query_async(&mut self.redis)
                  .await?;

              for job_data in result {
                  let job_key = format!("job:{}", hex::encode(&job_data[..8]));
                  
                  // Atomic move to processing
                  let moved: i32 = redis::cmd("LREM")
                      .arg(&format!("queue:{}", self.queue))
                      .arg(0)
                      .arg(&job_data)
                      .query_async(&mut self.redis)
                      .await?;

                  if moved == 0 {
                      continue; // Already processed by another worker
                  }

                  self.redis.set_ex(&job_key, &job_data, self.heartbeat_ttl).await?;
                  self.redis.hset(
                      &self.processing_key,
                      &job_key,
                      std::time::SystemTime::now()
                          .duration_since(std::time::UNIX_EPOCH)
                          .unwrap()
                          .as_secs()
                          .to_string()
                  ).await?;

                  let job = decode_job(&job_data);
                  
                  if let Err(e) = middleware.before_perform(&job).await {
                      self.handle_failure(&job_key, &job_data, e).await?;
                      continue;
                  }

                  match middleware.perform(&job).await {
                      Ok(()) => {
                          middleware.after_perform(&job).await;
                          self.redis.del(&job_key).await?;
                          self.redis.hdel(&self.processing_key, &job_key).await?;
                      }
                      Err(e) => {
                          middleware.after_failure(&job).await;
                          self.handle_failure(&job_key, &job_data, e).await?;
                      }
                  }
              }

              Ok(())
          }

          async fn handle_failure(
              &mut self,
              job_key: &str,
              job_data: &[u8],
              error: Box<dyn std::error::Error + Send + Sync>,
          ) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
              let retries: i32 = self.redis.hget(&self.processing_key, format!("{job_key}:retries")).await?;
              
              if retries >= 5 {
                  // Move to dead letter queue
                  self.redis.lpush("queue:failed", job_data).await?;
                  self.redis.del(job_key).await?;
                  self.redis.hdel(&self.processing_key, job_key).await?;
              } else {
                  self.redis.hincr(&self.processing_key, format!("{job_key}:retries"), 1).await?;
                  
                  // Requeue with backoff
                  let delay = 60 * 2u64.pow(retries as u32);
                  tokio::time::sleep(Duration::from_secs(delay)).await;
                  self.redis.lpush(&format!("queue:{}", self.queue), job_data).await?;
              }
              
              Ok(())
          }
      }

      pub trait Middleware: Send + Sync {
          fn before_enqueue(&self, _job: &Job) -> impl std::future::Future<Output = Result<(), Box<dyn std::error::Error + Send + Sync>>> + Send { async { Ok(()) } }
          fn after_enqueue(&self, _job: &Job) -> impl std::future::Future<Output = ()> + Send { async {} }
          fn before_perform(&self, _job: &Job) -> impl std::future::Future<Output = Result<(), Box<dyn std::error::Error + Send + Sync>>> + Send { async { Ok(()) } }
          fn after_perform(&self, _job: &Job) -> impl std::future::Future<Output = ()> + Send { async {} }
          fn after_failure(&self, _job: &Job) -> impl std::future::Future<Output = ()> + Send { async {} }
          fn perform(&self, job: &Job) -> impl std::future::Future<Output = Result<(), Box<dyn std::error::Error + Send + Sync>>> + Send;
      }

      fn decode_job(data: &[u8]) -> Job {
          Job::decode(data).unwrap_or_default()
      }

traps:
  - id: json_serialization
    description: Never use JSON for job serialization in production. Binary formats (protobuf, msgpack, cbor) are 5-10x faster and produce smaller payloads. JSON lacks schema validation and type safety.
  - id: blocking_redis_ops
    description: Never use blocking Redis operations in async Rust workers. Always use async commands (brpoplpush, rpush, etc.) or you will block the tokio runtime and degrade throughput.
  - id: missing_dlq
    description: Always implement a dead letter queue. Without DLQ, failed jobs are lost forever, making debugging impossible and causing data inconsistencies.
  - id: no_heartbeat
    description: Without heartbeat/visibility timeout, crashed workers cause jobs to hang forever. BRPOPLPUSH alone is not enough; you need active heartbeat extension.
  - id: unbounded_queue
    description: Never create unbounded queues in Redis. Always set max length (maxLen) or you risk Redis memory exhaustion. Use LTRIM or capped lists.
  - id: rate_limit_bypass
    description: Be aware that delayed/ETA jobs in BullMQ bypass rate limits by default. Schedule external rate limiting enforcement if delayed jobs must respect limits.
  - id: job_payload_size
    description: Keep job payloads small (<10KB). Large payloads bloat Redis memory and slow queue operations. Store large data in object storage and pass references.
  - id: connection_pool_exhaustion
    description: Configure connection pool size (min_idle, max_connections) appropriately. Each worker needs 1-2 connections minimum; undersized pools cause timeouts.
  - id: shutdown_timeout
    description: Always set a reasonable shutdown timeout. Without it, containers/VMs may kill your process ungracefully, leaving jobs in inconsistent state.
  - id: retry_storm
    description: Always add jitter to retry delays. Without jitter, many failing jobs retry simultaneously, overwhelming the system (thundering herd problem).

best_practices:
  - Use BRPOPLPUSH instead of simple BRPOP for reliable processing
  - Implement idempotent job handlers wherever possible
  - Keep job handlers stateless; serialize all state in job payload
  - Monitor queue depth, job duration histograms, and error rates
  - Use separate connections for pub/sub (subscriptions) vs regular commands
  - Set memory limits on Redis with maxmemory-policy to prevent runaway growth
  - Use Redis Cluster for horizontal scaling and fault tolerance
  - Implement circuit breakers for downstream service failures
  - Consider using Lua scripts for atomic multi-key operations
  - Use pipeline() for batch operations to reduce round trips

related_skills:
  - redis-fundamentals
  - distributed-systems-patterns
  - observability-monitoring
  - docker-kubernetes-deployment
  - service-mesh-istio
