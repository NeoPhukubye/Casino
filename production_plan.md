# Casino Bonus Scraper - Production Plan

## 1. Hosting/Compute
**Recommended: AWS Lambda + EventBridge + S3/CloudFront**

- **AWS Lambda**: Serverless execution for the scraper (Python runtime) with 512MB-1GB memory. Runs on-demand and scales automatically with no server management.
- **Why**: Cost-effective for scheduled scraping (just execution time), no idle costs, high availability, integrates well with EventBridge for scheduling.
- **Alternative**: ECS Fargate (if longer runtimes needed), Hetzner VPS ($5-20/month for small instance), Railway ($5-20/month). Lambda is optimal for < 15 min runs.

## 2. Database & Backups
**Recommended: PostgreSQL on Supabase (or Amazon RDS)**

- **Primary DB**: Supabase PostgreSQL (managed, includes connection pooling, easy API).
- **Schema**: Store casino_id, casino_name, welcome_bonus, wagering_requirement, minimum_deposit, source_url, scraped_at, updated_at.
- **Backups**: Supabase provides automatic daily backups; for RDS, enable automated backups with 7-35 day retention and point-in-time recovery (PITR).
- **Why**: Managed service with automated backups, monitoring, and cost-effective at small scale.

## 3. Infrastructure, Domain, DNS & HTTPS
**Recommended: Cloudflare + GitHub Pages (frontend) + AWS (backend)**

- **Frontend**: GitHub Pages for static hosting (free, integrates with Git repo, auto-deploy on push).
- **Custom Domain**: Purchase/register domain (e.g., Namecheap/Cloudflare Registrar ~$10/year).
- **DNS**: Cloudflare as DNS provider for DDoS protection, CDN caching, and page rules.
- **HTTPS**: Automatic HTTPS via Cloudflare (Universal SSL) and GitHub Pages provides HTTPS for *.github.io; with custom domain, Cloudflare provides SSL termination.
- **Why**: Free SSL, global CDN, security features, and cost-effective.

## 4. Scheduling & Monitoring
**Recommended: AWS EventBridge + SNS/Slack + Sentry**

- **Scheduling**: EventBridge rules trigger Lambda function daily (e.g., 00:00 UTC cron `0 0 * * ? *`).
- **Error Handling**: Capture exceptions in Lambda, send alerts to Slack via SNS/HTTPS webhook, and log to CloudWatch.
- **Monitoring**: CloudWatch Logs, CloudWatch Metrics (duration, errors, invocations), and Sentry for error tracking/alerting.
- **Alternative**: GitHub Actions cron (free, but limited to repo; for 200 casinos, may need longer timeout or self-hosted runner).
- **Why**: Reliable, serverless scheduling with comprehensive monitoring.

## 5. Cost Estimate (Target: $20-$50/month for 200 casinos)

| Component | Configuration | Estimated Monthly Cost | Notes |
|-----------|--------------|----------------------|-------|
| AWS Lambda | Daily runs (~5-10 min total), 1GB memory | $0.20 - $2.00 | Pay per invocation/execution time |
| AWS EventBridge | 1 scheduled rule | $0.00 - $1.00 | Usually free for first 1M events |
| S3 (data storage) | JSON backups/history | $0.01 - $0.50 | Minimal storage |
| CloudFront | CDN for API/data if needed | $0.00 - $5.00 | Based on requests/transfer |
| Supabase Postgres | Free tier → Pro if > limits | $0.00 - $25.00 | Free tier sufficient initially; Pro at higher scale |
| Cloudflare | DNS + SSL + CDN | $0.00 | Free plan covers needs |
| GitHub Pages | Frontend hosting | $0.00 | Free for public repos |
| Monitoring (Sentry) | Developer/Team plan | $0.00 - $9.00 | Free tier often sufficient |
| Domain | Registration | ~$0.80/month avg | ~$10/year |

**Total estimated: $5 - $30/month** (well under $20-$50 target). Costs scale with scraping frequency, data volume, and API usage.

## Implementation Notes
- **Rate limiting**: Add delays between requests, respect robots.txt, use rotating user agents if needed (but must stay ethical).
- **LLM costs**: Using `gpt-4o-mini` or `claude-3-5-haiku` is very cheap ($0.00015-0.00025/M input tokens) - ~200 casinos * small content = < $1/month.
- **Data freshness**: Daily scraping is sufficient; implement upsert logic in DB to avoid duplicates.
- **Failover**: Add retry logic with exponential backoff, circuit breakers for unreliable sources.
- **Security**: Store API keys in AWS Secrets Manager/Parameter Store, never commit .env files.
- **Compliance**: Only scrape publicly available data, respect ToS of sources, and ensure compliance with applicable laws/regulations.
