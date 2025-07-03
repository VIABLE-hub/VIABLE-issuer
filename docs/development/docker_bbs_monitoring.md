# BBS+ Docker Monitoring Guide

This guide explains how to use the monitoring tool for BBS+ in Docker containers. This tool continuously checks the health of BBS+ in running containers and alerts when issues are detected.

## Overview

The StudentVC system uses BBS+ signatures for credential issuance and verification. When running in Docker containers, platform-specific differences in the BBS+ module can cause issues. The monitoring tool helps detect these issues early, before they affect users.

## When to Use Monitoring

Use the monitoring tool in the following scenarios:

1. **Production Environments** - To ensure BBS+ is working correctly in production
2. **After Deployments** - To verify that BBS+ is working correctly after deploying new containers
3. **During Testing** - To detect BBS+ issues during testing
4. **Continuous Integration** - As part of a CI/CD pipeline to verify BBS+ functionality

## Prerequisites

- Docker running with StudentVC containers deployed
- Access to the host machine running the containers
- Terminal with bash support

## Using the Monitoring Tool

### Quick Start

Run the monitoring tool using:

```bash
make monitor-bbs
```

Or run the script directly:

```bash
./scripts/debugging/bbs_docker_monitor.sh
```

### How It Works

The monitoring tool:

1. **Detects** running StudentVC containers
2. **Checks** BBS+ functionality in each container at regular intervals
3. **Logs** the results to the console and a log file
4. **Alerts** when issues are detected after a configurable number of consecutive failures

### Configuration

The monitoring tool can be configured by editing the following variables at the top of the script:

```bash
# Configuration
CHECK_INTERVAL=60  # seconds between checks
LOG_FILE="bbs_monitor_$(date +%Y%m%d_%H%M%S).log"
ALERT_THRESHOLD=3  # number of consecutive failures before alerting
```

- `CHECK_INTERVAL`: Time in seconds between health checks
- `LOG_FILE`: Name of the log file (default includes timestamp)
- `ALERT_THRESHOLD`: Number of consecutive failures before sending an alert

### Alerts

When the monitoring tool detects an issue with BBS+ in a container, it:

1. Logs the issue to the console and log file
2. Displays an alert message in the terminal
3. Sends a desktop notification (if supported by the system)
4. Recommends running the hot-patching tool to fix the issue

### Log File

The monitoring tool creates a log file with all events, including:

- Start of monitoring
- Health check results
- Alerts
- Warnings

The log file is named `bbs_monitor_YYYYMMDD_HHMMSS.log` by default, where `YYYYMMDD_HHMMSS` is the timestamp when the monitoring started.

## Running in Background

To run the monitoring tool in the background, use:

```bash
nohup make monitor-bbs &
```

Or:

```bash
nohup ./scripts/debugging/bbs_docker_monitor.sh > monitor.out 2>&1 &
```

This will run the monitoring tool in the background and save the output to `monitor.out`.

## Integrating with Monitoring Systems

The monitoring tool can be integrated with monitoring systems like Prometheus, Nagios, or Zabbix by:

1. Parsing the log file for alerts
2. Using the exit code of the health check function
3. Sending alerts to a monitoring system API

For example, to check the health of BBS+ in a specific container:

```bash
./scripts/debugging/bbs_docker_monitor.sh --check-container <container_id>
```

## Troubleshooting

### No Containers Found

If the tool doesn't find any StudentVC containers, make sure they're running:

```bash
docker ps | grep studentvc
```

If no containers are running, start them:

```bash
make docker-run
```

### False Positives

If the tool reports false positives (alerts when BBS+ is actually working), try:

1. Increasing the `ALERT_THRESHOLD` to require more consecutive failures
2. Checking if the container is under heavy load
3. Verifying that BBS+ is installed correctly

### False Negatives

If the tool doesn't detect actual BBS+ issues, try:

1. Decreasing the `CHECK_INTERVAL` to check more frequently
2. Verifying that the health check is testing all required functionality
3. Adding more comprehensive tests to the health check function

## Conclusion

The BBS+ Docker monitoring tool provides continuous monitoring of BBS+ functionality in Docker containers. By detecting issues early, it helps ensure that your StudentVC system remains operational and that users don't experience credential issuance or verification failures. 